import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(funcName)s -> %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def main():
	with safe_connect() as cur:
		setup_db(cur)

		insert_to_db(cur, "https://news.ycombinator.com/")
		insert_to_db(cur, "https://hn.algolia.com/")
		logger.info("Job inserido com sucesso.")

"""	with safe_connect() as cur:
		job = dequeue(cur)
		logger.info("Job capturado pelo dequeue: %s", job)

		if job:
			job_id, url = job

			update_db(cur, job_id, "processed")
			logger.info("Job %s atualizado para processed.", job_id)"""




@contextmanager
def safe_connect():
	with sqlite3.connect("fix.db") as con:
		cur = con.cursor()
		try:
			yield cur
			con.commit()

		except Exception as e:
			logger.error("An error ocurred: %s", e)
			con.rollback()
			raise


def setup_db(cur):
	cur.execute("""
		CREATE TABLE IF NOT EXISTS jobs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			url TEXT NOT NULL,
			status TEXT NOT NULL)
		""")


def insert_to_db(cur, url):
	cur.execute("""
		INSERT INTO jobs (url, status) VALUES(?, ?)
		""", (url, "pending"))


def dequeue(cur):
    cur.execute("""
        UPDATE jobs
        SET status = "processing"
        WHERE id = (
            SELECT id FROM jobs
            WHERE status = "pending"
            ORDER BY id
            LIMIT 1
        )
        AND status = "pending"
        RETURNING id, url
        """)
    return cur.fetchone()


def update_db(cur, id, status):
	cur.execute("""
		UPDATE jobs
		SET status = ?
		WHERE id = ?
		""", (status, id))


if __name__ == "__main__":
	main()
