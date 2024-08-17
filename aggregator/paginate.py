from typing import Generic, List, TypeVar

from pydantic.generics import GenericModel

OutSchema = TypeVar("OutSchema")


class Paginate(GenericModel, Generic[OutSchema]):
    page: int = 1
    perPage: int = 10
    total: int = 0
    results: List[OutSchema]

    @property
    def pages(self) -> int:
        return self.total // self.perPage + (self.total % self.perPage > 0)
