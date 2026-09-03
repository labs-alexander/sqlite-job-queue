import sqlite3
import asyncio


class SetupDB:
	@classmethod
	def setup_db(cls, db_path):
		with sqlite3.connect(db_path) as con:
			con.execute("""
				CREATE TABLE IF NOT EXISTS jobs(
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					status TEXT NOT NULL DEFAULT 'pending',
					tries INTEGER NOT NULL DEFAULT 0,
					available_at TEXT,
					url TEXT NOT NULL
					)""")


class Job:
	def __init__(self):
		...


	def __enter__(self):
		self.con = sqlite3.connect("queue.db")
		self.cur = self.con.cursor()
		print("Connection open.")
		return self


	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			self.con.commit()
			self.con.close()
			print("Connection closed")
		else:
			self.con.rollback()
			self.con.close()
			print("Something went wrong during the management of the database.\nDoing rollback.")


	def insert_to_db(self, url):
		self.cur.execute("""
			INSERT INTO jobs (url) VALUES (?)
			""", (url,))


	def dequeue(self, limit):
		self.cur.execute("""
			UPDATE jobs
			SET status = "processing"
			WHERE id IN (SELECT id FROM jobs WHERE status = "pending" LIMIT ?)
			RETURNING id, url
			""", (limit,))

		return self.cur.fetchall()



async def main():
	print("Running test ->")
	SetupDB.setup_db("queue.db")
	with Job() as job:
		job.insert_to_db("https://hn.algolia.com/")
		print(job.dequeue(1))
		print("End of test")
		


if __name__ == "__main__":
	asyncio.run(main())
