import logging
from logging.config import fileConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logging.config.fileConfig("logging.conf")

# 获取配置好的日志记录器
logger = logging.getLogger("myLogger")
logger.debug('debug')
logger.info('info')
logger.warning('warn')
logger.error('error')
logger.critical('critical')

