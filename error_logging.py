import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
	root = logging.getLogger()
	root.setLevel(logging.DEBUG)

	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s-> %(message)s"))

	file_handler = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s-> %(name)s:%(funcName)s:%(lineno)d %(message)s"))

	root.addHandler(console)
	root.addHandler(file_handler)

	return root


if __name__ == "__main__":
	pass
