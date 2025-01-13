from logging import (DEBUG, INFO, FileHandler, Formatter, StreamHandler,
                     getLogger)


def get_module_logger(module):
    logger = getLogger(module)
    logger = _set_handler(logger, StreamHandler(), False)
    logger.setLevel(DEBUG)
    logger.propagate = False
    return logger


def _set_handler(logger, handler, verbose):
    if verbose:
        handler.setLevel(DEBUG)
        handler.setFormatter(
            Formatter(
                "[%(asctime)s %(name)s][%(lineno)s][%(funcName)s][%(levelname)s] %(message)s"
            )
        )
    else:
        handler.setLevel(INFO)
        handler.setFormatter(
            Formatter("[%(asctime)s %(name)s][%(levelname)s] %(message)s")
        )
    logger.addHandler(handler)
    return logger
