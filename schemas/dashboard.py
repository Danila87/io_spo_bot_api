from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class Dashboard(BaseModel):

    id: int
    uid : str = Field(description="uid Дашборда", title="uid Дашборда")
    title: str = Field(description="Название дашборда", title="Название дашборда")
    tags: Optional[List[str]] = Field(description="Теги дашборда", title="Теги дашборда")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uid": "dashboard-uid",
                "title": "ИО СПО БОТ",
                "tags": ["tag1", "tag2"]
            }
        }
    )


class Visualization(BaseModel):
    id: int
    title: str

    dashboard_uid: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Топ 5 за месяц",
                "dashboard_uid": "dashboard-uid"
            }
        }
    )
