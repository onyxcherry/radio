from abc import abstractmethod
from dataclasses import field


class Serializable:

    @abstractmethod
    def to_json(self):
        pass


class Event(Serializable):
    pass


# class Event:
#     def __init__(self, created: Optional[datetime]):
#         print("Wykonało się w ogóle?")
#         if created is None:
#             created = datetime.now(tz=timezone.utc)
#         self.created = created

#     # @property
#     # def created(self):
#     #     return self._created

#     # @created.setter
#     # def created(self, value):
#     #     self._created = value
