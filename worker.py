import queue_db as q
import sys
import asyncio
import logging
from typing import NamedTuple
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class Job(NamedTuple):
	id: int
	url: str
	tries: int


async def main():
	try:
		async with AsyncSession() as session:
			while True:
				row = await asyncio.to_thread(dequeue_job)
				if not row:
					logger.info("job not found, waiting 1 seconds.")
					await asyncio.sleep(1)		
					continue
				
				job = Job(*row)
				response = await process_job(session ,job.url)
				
				await parser(response, job)

	except (KeyboardInterrupt, asyncio.CancelledError):
		sys.exit(0)


def dequeue_job():
	with q.safe_connect() as cur:
		return q.dequeue(cur)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    reraise=True
)
async def fetch(session, url):
	response = await session.get(url, impersonate="firefox")
	response.raise_for_status()
	return response


def _save_status(job_id: int, status: str):
    with q.safe_connect() as cur:
        q.update_db(cur, job_id, status)


def _parse_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return soup.title.string.strip() if soup.title else "No title found"


async def parser(response, job):
    if not response:
        await asyncio.to_thread(_save_status, job.id, "failed")
        return

    title = await asyncio.to_thread(_parse_title, response.text)
    logger.info("Fetch result for url %s: %s:\n-> %s", job.id, job.url, title)

    status = "processed" if title and title != "No title found" else "failed"
    await asyncio.to_thread(_save_status, job.id, status)


async def process_job(session, url):
    try:
        return await fetch(session, url)
    except Exception as e:
        response = getattr(e, "response", None)
        if response is not None and 400 <= response.status_code < 500:
            return None

        raise


if __name__ == "__main__":
	asyncio.run(main())
