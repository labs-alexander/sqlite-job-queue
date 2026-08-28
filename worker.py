import queue_db as q
import sys
import time
import logging
from bs4 import BeautifulSoup
from curl_cffi import requests
from typing import NamedTuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class Job(NamedTuple):
	id: int
	url: str
	tries: int


def main():
	try:
		while True:
			row = dequeue_job()
			if not row:
				logger.info("job not found, waiting 1 seconds.")
				time.sleep(1)		
				continue
			
			job = Job(*row)
			response = process_job(job.url)
			
			parser(response, job)

	except KeyboardInterrupt:
		sys.exit(0)


def dequeue_job():
	with q.safe_connect() as cur:
		return q.dequeue(cur)


@retry(
	stop=stop_after_attempt(5),
	wait=wait_exponential(multiplier=1, min=2, max=5),
	reraise=True
)		
def fetch(url):
	response = requests.get(url, impersonate="firefox")
	response.raise_for_status()
	return response


def parser(response, job):
	if not response:
		with q.safe_connect() as cur:
			q.update_db(cur, job.id, "failed")

		return

	soup = BeautifulSoup(response.text, "lxml")
	title = soup.title.string.strip() if soup.title else "No title found"
	logger.info("Fetch result for url %s: %s:\n-> %s",job.id, job.url, title)

	if title and title != "No title found":
		with q.safe_connect() as cur:
			q.update_db(cur, job.id, "processed")

	else:
		with q.safe_connect() as cur:
			q.update_db(cur, job.id, "failed")


def process_job(url):
    try:
        return fetch(url)
    except Exception as e:
        response = getattr(e, "response", None)
        if response is not None and 400 <= response.status_code < 500:
            return None

        raise


if __name__ == "__main__":
	main()
