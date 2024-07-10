from abc import abstractmethod


class Serializable:

    @abstractmethod
    def to_bytes(self):
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
