import dataclasses
from datetime import date, datetime
from json import JSONEncoder
from uuid import UUID


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif dataclasses.is_dataclass(type(obj)):
            return dataclasses.asdict(obj)
        elif isinstance(obj, list):
            return list(self.default(elem) for elem in obj)
        else:
            return super().default(obj)
