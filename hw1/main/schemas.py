from typing import List, Optional

from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    title: str
    quantity: int
    unit: str
    description: Optional[str] = Field(default="")

    model_config = {
        "from_attributes": True
    }


class RecipeBase(BaseModel):
    title: str
    preparation_time: int
    views: int = 0

    model_config = {
        "from_attributes": True
    }


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientBase]
    description: str = Field(default="")


class Recipe(RecipeBase):
    id: int
    ingredients: List[IngredientBase]

    model_config = {
        "from_attributes": True
    }


class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    model_config = {
        "from_attributes": True
    }


class RecipeDetail(RecipeBase):
    id: int
    ingredients: List[IngredientBase]
    description: str = Field(default="")

    model_config = {
        "from_attributes": True
    }
