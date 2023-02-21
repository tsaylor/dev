import logging, json


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            obj = [a for a in obj]
        elif isinstance(obj, Task):
            obj = str(obj)
        return obj


ATTR_TO_JSON = ["msg", "complete", "exec_tree", "runnable"]


class JSONFormatter:
    def format(self, record):
        obj = {
            attr: getattr(record, attr)
            for attr in ATTR_TO_JSON
            if hasattr(record, attr)
        }
        # obj = dict(**record.__dict__)
        return json.dumps(obj, indent=4, cls=SetEncoder)


def configure_logging(level=logging.INFO):
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(JSONFormatter())

    rootlogger = logging.getLogger()
    rootlogger.addHandler(logHandler)
    rootlogger.setLevel(level)

def get_logger(name):
    return logging.getLogger(__name__)