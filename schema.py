from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseRecipe(BaseModel):
    title: str = Field(..., description="Название блюда", examples=["Борщ"])
    cooking_time: int = Field(..., description="Время приготовления в минутах", gt=0)
    ingredients: str = Field(..., description="Список ингредиентов одной строкой")
    description: Optional[str] = Field(None, description="Текстовое описание рецепта")


class RecipeCreate(BaseRecipe):
    pass


class RecipeOut(BaseRecipe):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Уникальный идентификатор рецепта")


class ShortRecipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., description="Название блюда", examples=["Борщ"])
    views: int = Field(
        ..., description="Количество просмотров детальной страницы рецепта"
    )
    cooking_time: int = Field(..., description="Время приготовления в минутах", gt=0)
