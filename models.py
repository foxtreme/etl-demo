from datetime import datetime
from pydantic import BaseModel


class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    language: str | None
    stars: int
    forks: int
    open_issues: int
    created_at: datetime
    updated_at: datetime
