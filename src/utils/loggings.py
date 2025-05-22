from logging import DEBUG, Formatter, StreamHandler, getLogger

__all__ = ["logger"]

logger = getLogger(__file__)
if not logger.handlers:
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
