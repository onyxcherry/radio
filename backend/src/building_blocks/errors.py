from dataclasses import dataclass
from typing import Self


class DomainError(Exception):
    pass


class ResourceNotFound(DomainError):
    pass


class RepositoryError(DomainError):
    @classmethod
    def save_operation_failed(cls) -> Self:
        return cls("An error occurred during saving to the database!")

    @classmethod
    def get_operation_failed(cls) -> Self:
        return cls("An error occurred while retrieving the data from the database!")


@dataclass
class APIErrorMessage:
    type: str
    message: str
