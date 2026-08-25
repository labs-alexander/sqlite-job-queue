import fix
import time
import logging
from bs4 import BeautifulSoup
from curl_cffi import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

while True:
	with fix.safe_connect() as cur:
		job = fix.dequeue(cur)
		print(job)
	if not job:
		time.sleep(10)
		logger.info("waiting 10 seconds, job not found.")
		continue

	job_id, url = job
	title = None
	try:
		response = requests.get(url, impersonate="firefox")
		code = response.status_code

		if code == 200:
			soup = BeautifulSoup(response.text, "lxml")
			title = soup.title.string.strip() if soup.title else "No title found"
			logger.info("Fetch result for url %s: %s:\n-> %s",job_id, url, title)
		else:
			logger.error("couldn't fetch the url -> %s: %s", job_id, url)

	except Exception:
		logger.error("unknown error occurred, process failed. url %s: %s", job_id, url)



	if title and not title == "No title found":
		with fix.safe_connect() as cur:
			fix.update_db(cur, job_id, "processed")
	else:
		with fix.safe_connect() as cur:
			fix.update_db(cur, job_id, "failed")
