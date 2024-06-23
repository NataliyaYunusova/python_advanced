from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.future import select

from . import models, schemas
from .database import DATABASE_URL, get_session

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
default_session = Depends(get_session)


@asynccontextmanager
async def lifespan(_application: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/recipes/", response_model=schemas.RecipeBase)
async def create_recipes(
        recipe: schemas.RecipeCreate,
        session: AsyncSession = default_session,
) -> schemas.RecipeBase:
    new_recipe = models.Recipe(
        title=recipe.title,
        preparation_time=recipe.preparation_time,
        description=recipe.description,
        views=recipe.views,
    )
    session.add(new_recipe)

    for ingredient in recipe.ingredients:
        new_ingredient = models.Ingredient(
            title=ingredient.title,
            quantity=ingredient.quantity,
            unit=ingredient.unit,
            description=ingredient.description,
            recipe=new_recipe,
        )
        session.add(new_ingredient)
    await session.commit()

    return schemas.RecipeBase(
        title=str(new_recipe.title),
        preparation_time=int(new_recipe.preparation_time),
        views=int(new_recipe.views),
    )


@app.get("/recipes/", response_model=List[schemas.RecipeBase])
async def get_recipes(
    session: AsyncSession = default_session,
) -> List[schemas.RecipeBase]:
    recipes_result = await session.execute(
        select(
            models.Recipe.title,
            models.Recipe.views,
            models.Recipe.preparation_time,
        ).order_by(
            models.Recipe.views.desc(),
            models.Recipe.preparation_time,
        )
    )

    recipes = recipes_result.all()

    await session.execute(
        update(models.Recipe)
        .values(views=models.Recipe.views + 1)
    )
    await session.commit()

    return [
        schemas.RecipeBase(
            title=recipe.title,
            preparation_time=recipe.preparation_time,
            views=recipe.views,
        )
        for recipe in recipes
    ]


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
async def get_recipe_detail(
        recipe_id: int,
        session: AsyncSession = default_session,
) -> schemas.RecipeDetail:
    recipe = await session.get(models.Recipe, recipe_id)

    if recipe is None:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="Recipe not found",
        )

    await session.execute(
        update(models.Recipe)
        .where(models.Recipe.id == recipe_id)
        .values(views=models.Recipe.views + 1)
    )
    await session.commit()

    ingredients_result = await session.execute(
        select(models.Ingredient)
        .where(models.Ingredient.recipe_id == recipe_id)
    )
    ingredients = ingredients_result.scalars().all()
    ingredient_list = [
        schemas.IngredientBase(
            title=str(ingredient.title),
            quantity=int(ingredient.quantity),
            unit=str(ingredient.unit),
            description=str(ingredient.description),
        )
        for ingredient in ingredients
    ]

    return schemas.RecipeDetail(
        id=int(recipe.id),
        title=str(recipe.title),
        preparation_time=int(recipe.preparation_time),
        views=int(recipe.views),
        description=str(recipe.description),
        ingredients=ingredient_list,
    )
