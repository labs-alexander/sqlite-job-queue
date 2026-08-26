import subprocess
import sys
import time
import signal
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKERS = 4

def main():
	processes = []

	#logger.info()

	for i in range(WORKERS):
		p = subprocess.Popen([sys.executable, "worker.py"])
		processes.append(p)
		logger.info("worker %d created PID: %d", i + 1, p.pid)

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		logger.info("stoping (CTRL+C)")

		for p in processes:
			p.terminate()

		for p in processes:	
			try:
				p.wait(timeout=2)
			except subprocess.TimeoutExpired:
				p.kill()

		logger.info("all workers have  been shut down")

if __name__ == "__main__":
	main()
