import q
import time
from curl_cffi import requests
from bs4 import BeautifulSoup


def process_job(job):
	response = requests.get(url=job, impersonate="firefox")
	soup = BeautifulSoup(response.text, "lxml")
	title = soup.title.string
	if title:
		return title
	return None


def main():
	with q.setup_db() as cur:
		q.insert_to_queue(cur, "https://hn.algolia.com/")
		while True:
			result = q.dequeue(cur)
			if result:
				id, url = result
				print("cheguei aqui s")
				print(type(url))
				title = process_job(url)
				print("cheguei aqui nao")
				if title:
					q.update_status(cur, id, "processed")
					print(f"successfully processed\nPage title: {title}")
				else:
					q.update_status(cur, id, "failed")
					print("couldnt process the page title")
			else:
				#time.sleep(2)
				print("No results")
				break


if __name__ == "__main__":
	main()
