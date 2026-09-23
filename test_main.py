import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from database import Base, engine
from main import app


@pytest_asyncio.fixture(scope="module")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_recipe(client):
    recipe_data = {
        "title": "Test Recipe",
        "cooking_time": 30,
        "ingredients": "Ingredient 1, Ingredient 2",
        "description": "Step 1, Step 2",
    }

    response = await client.post("/recipes", json=recipe_data)

    assert response.status_code == 201
    assert response.json()["title"] == recipe_data["title"]


@pytest.mark.asyncio
async def test_get_recipes(client):
    response = await client.get("/recipes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_recipe(client):
    recipe_data = {
        "title": "Another Test Recipe",
        "cooking_time": 45,
        "ingredients": "Ingredient A, Ingredient B",
        "description": "Step A, Step B",
    }

    create_response = await client.post("/recipes", json=recipe_data)
    recipe_id = create_response.json()["id"]

    response = await client.get(f"/recipes/{recipe_id}")

    assert response.status_code == 200
    assert response.json()["id"] == recipe_id


@pytest.mark.asyncio
async def test_get_nonexistent_recipe(client):
    response = await client.get("/recipes/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Рецепт не найден"
