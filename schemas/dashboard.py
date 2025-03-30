from pydantic import BaseModel, Field
from typing import Optional, List

class Dashboard(BaseModel):

    id: int
    uid : str = Field(description="uid Дашборда", title="uid Дашборда")
    title: str = Field(description="Название дашборда", title="Название дашборда")
    tags: Optional[List[str]] = Field(description="Теги дашборда", title="Теги дашборда")

class Visualization(BaseModel):
    id: int
    title: str

    dashboard_uid: str