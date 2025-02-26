import dataclasses
import pydantic
from json import JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(type(obj)):
            return dataclasses.asdict(obj)
        return pydantic.RootModel[type(obj)](obj).model_dump(by_alias=True, mode="json")
