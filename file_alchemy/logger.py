import logging


logger = logging.getLogger('file_alchemy')
logger.setLevel(logging.DEBUG)

formater = logging.Formatter("[%(levelname)s] - %(asctime)s - %(message)s")

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formater)

logger.addHandler(sh)