from pydantic import BaseModel, ConfigDict


class ThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    icon: str
