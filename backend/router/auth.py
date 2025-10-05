from fastapi import APIRouter, Depends, HTTPException
from schemas.auth import SUserRegister, SUserLogin, SUser, SAssignRole
from repositories.auth import UserRepository
from models.auth import UserOrm
from utils.security import create_access_token, get_current_user, oauth2_scheme, get_current_admin




router = APIRouter(
    prefix="/auth",
    tags=['Пользователи']
)


@router.post("/register")
async def register_user(user_data: SUserRegister):
    try:
        user_id = await UserRepository.register_user(user_data)
        return {"success": True, "user_id": user_id, "message": "Регистрация прошла успешно"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_user(login_data: SUserLogin):
    user = await UserRepository.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = await UserRepository.create_refresh_token(user.id)
    return {"success": True, "message": "Вы вошли в аккаунт", "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    user = await UserRepository.get_user_by_refresh_token(refresh_token)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный refresh токен")
    
    new_access_token = create_access_token(data={"sub": user.email})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), current_user: UserOrm = Depends(get_current_user)):
    await UserRepository.add_to_blacklist(token)
    await UserRepository.revoke_refresh_token(current_user.id)
    return {"success": True}


@router.get("/me", response_model=SUser)
async def get_current_user_info(current_user: UserOrm = Depends(get_current_user)):
    fresh_user = await UserRepository.get_user_by_id(current_user.id)
    return SUser.model_validate(fresh_user)


@router.post("/assign-role")
async def assign_role(role_data: SAssignRole, current_user: UserOrm = Depends(get_current_admin)):
    try:
        if role_data.user_id == current_user.id and role_data.role_id != 2:
            raise HTTPException(
                status_code=400, 
                detail="Вы не можете снять себе права администратора"
            )
        
        await UserRepository.assign_user_role(role_data.user_id, role_data.role_id)
        return {
            "success": True, 
            "message": "Роль успешно назначена. Пользователю требуется перелогин."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))