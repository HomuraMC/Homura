from logging import getLogger, Formatter, StreamHandler, FileHandler, DEBUG, INFO

def get_module_logger(module, verbose):
	logger = getLogger(module)
	logger = _set_handler(logger, StreamHandler(), False)
	logger.setLevel(DEBUG)
	logger.propagate = False
	return logger


def _set_handler(logger, handler, verbose):
	if verbose:
		handler.setLevel(DEBUG)
	else:
		handler.setLevel(INFO)
	handler.setFormatter(Formatter('%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s'))
	logger.addHandler(handler)
	return logger