import datetime
import logging
import sys

# ログレベルごとに色を定義
LOG_COLORS = {
    logging.DEBUG: "\033[94m",  # 青色
    logging.INFO: "\033[0m",  # 無色
    logging.WARNING: "\033[33m",  # 黄色
    logging.ERROR: "\033[31m",  # 赤色
    logging.CRITICAL: "\033[95m",  # 紫色
}


# カスタムのStreamHandlerを作成し、色を適用
class ColoredStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            self.stream.write(LOG_COLORS[record.levelno])
            super().emit(record)
        finally:
            self.stream.write("\033[0m")


class log:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    dt = datetime.datetime.now()
    formatter = logging.Formatter(
        "[{}] %(levelname)s %(message)s".format(dt.strftime("%H:%M:%S"))
    )
    handler = ColoredStreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
