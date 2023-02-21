import logging
import logging.config
import json
ATTR_TO_JSON = ['created', 'filename', 'funcName', 'levelname', 'lineno', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'thread', 'threadName']
class JsonFormatter:
    def format(self, record):
        obj = {attr: getattr(record, attr)
                  for attr in ATTR_TO_JSON}
        # obj = dict(**record.__dict__)
        return json.dumps(obj, indent=4)

handler = logging.StreamHandler()
handler.formatter = JsonFormatter()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.error("Hello", extra={})
