from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
from models import Recipe
from schema import RecipeCreate, RecipeOut, ShortRecipe


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Создание всех таблиц в базе данных при старте приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get(
    "/recipes",
    response_model=list[ShortRecipe],
    summary="Получить все рецепты",
    description="Возвращает список всех рецептов, отсортированных по количеству просмотров и времени приготовления.",
)
async def get_recipes(db: AsyncSession = Depends(get_db)):
    """
    Получение списка всех рецептов.
      db: Сессия базы данных.
    Возвращает список объектов `ShortRecipe`.
    """
    recipes = await db.execute(
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time)
    )
    return recipes.scalars().all()


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Получить рецепт по ID",
    description="Возвращает рецепт по указанному ID.",
)
async def get_recipes_by_id(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получение рецепта по его ID.
        recipe_id: ID рецепта.
        db: Сессия базы данных.
    Возвращает объект `RecipeOut` или вызывает ошибку 404, если рецепт не найден.
    """

    recipe = await db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден"
        )
    try:
        await db.execute(
            update(Recipe).where(Recipe.id == recipe_id).values(views=Recipe.views + 1)
        )
        await db.commit()
        await db.refresh(recipe)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return recipe


@app.post(
    "/recipes",
    response_model=RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создает новый рецепт и возвращает его.",
)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    """
    Создание нового рецепта.
        recipe: Объект `RecipeCreate`, содержащий данные нового рецепта.
        db: Сессия базы данных.
    Возвращает созданный объект `RecipeOut`.
    """
    new_recipe = Recipe(**recipe.model_dump())
    db.add(new_recipe)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    await db.refresh(new_recipe)
    return new_recipe
