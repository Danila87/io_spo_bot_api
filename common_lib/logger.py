import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('iospobot_api')
logger.setLevel(logging.INFO)

log_handler = TimedRotatingFileHandler(
    filename=f'logs/{datetime.now().date()}.log',
    interval=1,
    backupCount=10,
    encoding='utf-8',
    when='midnight',
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)
