import asyncio
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..main.app import app as fastapi_app
from ..main.app import models
from ..main.database import Base, get_session

DATABASE_URL_TEST = "sqlite+aiosqlite:///test_app.db"

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    class_=AsyncSession
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

fastapi_app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            recipe = models.Recipe(
                title="Test Recipe",
                preparation_time=10,
                views=0,
                description="Test description",
            )
            session.add(recipe)
            await session.commit()

            assert recipe.id is not None, "Recipe ID should be set after commit"

            ingredient = models.Ingredient(
                title="Test Ingredient",
                quantity=1,
                unit="unit",
                description="Ingredient description",
                recipe_id=recipe.id
            )
            session.add(ingredient)

            await session.commit()
            await session.refresh(recipe)
    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
def app() -> FastAPI:
    return fastapi_app


@pytest.fixture(scope="module")
async def async_client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
