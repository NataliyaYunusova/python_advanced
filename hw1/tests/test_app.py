import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..main.models import Ingredient, Recipe


@pytest.fixture(scope="function")
async def setup_recipe(async_client: AsyncClient, session: AsyncSession):
    recipe = Recipe(
        title="Test Recipe",
        preparation_time=10,
        views=0,
        description="Test description"
    )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)

    ingredient = Ingredient(
        title="Ingredient 1",
        quantity=1,
        unit="pcs",
        description="Test Ingredient 1",
        recipe_id=recipe.id
    )
    session.add(ingredient)
    await session.commit()
    await session.refresh(ingredient)

    return recipe


@pytest.mark.anyio
async def test_create_recipe(async_client: AsyncClient):
    recipe_data = {
        "title": "New Test Recipe",
        "preparation_time": 10,
        "views": 0,
        "ingredients": [
            {
                "title": "New Ingredient 1",
                "quantity": 1,
                "unit": "pcs",
                "description": "New Test Ingredient 1"
            }
        ],
        "description": "New Test description"
    }
    response = await async_client.post("/recipes/", json=recipe_data)
    assert response.status_code == 200
    assert response.json()["title"] == "New Test Recipe"


@pytest.mark.anyio
async def test_get_recipe_detail(async_client: AsyncClient, session):
    response = await async_client.get("/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Recipe"
    assert data["description"] == "Test description"
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["title"] == "Test Ingredient"
