import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables, delete_tables, new_session
from router.auth import router as auth_router
from router.mark import router as mark_router
from kafka_consumer import consume_marks

from fastapi import APIRouter
from repositories.auth import UserRepository
from schemas.auth import SUserRegister
from models.auth import RoleOrm, UserOrm
from sqlalchemy import select




@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База данных очищена")
    await create_tables()
    print("Таблицы созданы")
    
    # Инициализация ролей
    async with new_session() as session:
        roles = [RoleOrm(role='user'), RoleOrm(role='admin')]
        session.add_all(roles)
        await session.commit()
        
        asyncio.create_task(consume_marks())
    
    print('База готова к работе')
    yield
    print('Выключение')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="2GIS Marks API",
        version="1.0.0",
        description="API for Marks functionality",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    secured_paths = {
        #Авторизация
        "/auth/me": {"method": "get", "security": [{"Bearer": []}]},
        "/auth/logout": {"method": "post", "security": [{"Bearer": []}]},
        "/auth/assign-role": {"method": "post", "security": [{"Bearer": []}]},
        "/marks/update/{mark_id}": {"method": "put", "security": [{"Bearer": []}]},
        "/marks/delete/{mark_id}": {"method": "delete", "security": [{"Bearer": []}]},
    }
    
    for path, config in secured_paths.items():
        if path in openapi_schema["paths"]:
            openapi_schema["paths"][path][config["method"]]["security"] = config["security"]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(lifespan=lifespan)
app.openapi = custom_openapi
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Тут адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_router = APIRouter()

@init_router.post("/init-test-data")
async def init_test_data():
    async with new_session() as session:
        # Проверяем, есть ли уже тестовые пользователи
        query = select(UserOrm).where(UserOrm.email.in_(["user@example.com", "admin@example.com"]))
        result = await session.execute(query)
        existing_users = result.scalars().all()
        
        if existing_users:
            return {"message": "Тестовые пользователи уже существуют"}
        
        # Создаем хэши паролей
        from utils.security import pwd_context  # ДОБАВЛЕНО
        user_password_hash = pwd_context.hash("string")
        admin_password_hash = pwd_context.hash("admin")
        
        # Создаем пользователей напрямую
        user = UserOrm(
            username="user",
            email="user@example.com",
            hashed_password=user_password_hash,
            role_id=1  # user role
        )
        
        admin = UserOrm(
            username="admin", 
            email="admin@example.com",
            hashed_password=admin_password_hash,
            role_id=2  # admin role
        )
        
        session.add_all([user, admin])
        await session.commit()
    
    return {"message": "Тестовые данные созданы"}



app.include_router(init_router)
app.include_router(mark_router)



#Раскоментить, когда будешь писать докер.
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        port=3001,
        host="0.0.0.0"
    )