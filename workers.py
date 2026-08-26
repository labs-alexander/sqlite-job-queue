import queue_db as q
import sys
import time
import logging
from bs4 import BeautifulSoup
from curl_cffi import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
	try:
		while True:
			job = dequeue_job()
			if not job:
				logger.info("job not found, waiting 1 seconds.")
				time.sleep(1)		
				continue
			
			job_id, url = job
			response = fetch(job_id, url)
			
			parser(response, job_id, url)

	except KeyboardInterrupt:
		sys.exit(0)


def dequeue_job():
	with q.safe_connect() as cur:
		return q.dequeue(cur)


def fetch(job_id, url):
	try:
		response = requests.get(url, impersonate="firefox")
		code = response.status_code

		if code == 200:
			return response.text

		else:
			logger.error("couldn't fetch the url -> %s: %s", job_id, url)

	except Exception:
		logger.error("unknown error occurred, process failed. url %s: %s", job_id, url)

	return None


def parser(response, job_id, url):
	if not response:
		with q.safe_connect() as cur:
			q.update_db(cur, job_id, "failed")

		return

	soup = BeautifulSoup(response, "lxml")
	title = soup.title.string.strip() if soup.title else "No title found"
	logger.info("Fetch result for url %s: %s:\n-> %s",job_id, url, title)

	if title and title != "No title found":
		with q.safe_connect() as cur:
			q.update_db(cur, job_id, "processed")

	else:
		with q.safe_connect() as cur:
			q.update_db(cur, job_id, "failed")


if __name__ == "__main__":
	main()
