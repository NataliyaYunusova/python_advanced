from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    preparation_time = Column(Integer)
    description = Column(String, default="")
    views = Column(Integer, default=0)

    ingredients = relationship("Ingredient", back_populates="recipe")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    quantity = Column(Integer)
    unit = Column(String)
    description = Column(String, default="")

    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = relationship("Recipe", back_populates="ingredients")
