import sqlite3
import logging

from contextlib import contextmanager

logger = logging.getLogger(__name__)

logging.basicConfig(
	level="DEBUG",
	format="%(asctime)s [%(levelname)s]\n'%(funcName)s -> %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
	filename="app.log",
	filemode="a"
	)


def main():
	with setup_db() as cur:
		setup_tables(cur)


# funçao que cria tabela se nao existir
def setup_tables(cur):
	cur.execute("""
		CREATE TABLE IF NOT EXISTS jobs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			job TEXT NOT NULL,
			status TEXT
			)
		""")


def insert_to_queue(cur, job):
	cur.execute("""
		INSERT INTO jobs(job, status) VALUES(?, ?)""",(job, "pending"))


def dequeue(cur):
	cur.execute("""
		UPDATE jobs
		SET status = "processing"
		WHERE id = (SELECT id FROM jobs WHERE status = "pending" ORDER BY id LIMIT 1)
		AND status = "pending"
		RETURNING id, job
		""")
	return cur.fetchone()


def name(cur, id, status):
	cur.execute("""
		UPDATE jobs
		SET status = ?
		WHERE id = ?
		"""(status, id)
		)


@contextmanager
def setup_db():
	with sqlite3.connect("queue.db") as con:
		try:			
			cur = con.cursor()
			yield cur
		except Exception as e:
			con.rollback()
			logger.error("An error occurred: %s ", e)
			raise

if __name__ == "__main__":
	main()
