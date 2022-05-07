import typing
import uuid

from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic.types import UUID4


class BaseDBModel(BaseModel):
    created_by: UUID4
    id: UUID4 = Field(default_factory=uuid.uuid4)


BDBM = typing.TypeVar("BDBM", bound=BaseDBModel)
