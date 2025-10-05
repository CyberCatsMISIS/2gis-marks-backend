from fastapi import APIRouter, Depends, HTTPException
from schemas.mark import SMark, SMarkCreate, SMarkUpdate
from repositories.mark import MarkRepository
from models.auth import UserOrm
from utils.security import get_current_admin




router = APIRouter(
    prefix="/marks",
    tags=['Заметки']
)



@router.get("/", response_model=list[SMark])
async def get_all_marks(limit: int = 10, offset: int = 0):
    try:
        marks = await MarkRepository.get_all_marks(limit, offset)
        return [SMark.model_validate(mark, from_attributes=True) for mark in marks]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{mark_id}", response_model=SMark)
async def get_mark_by_id(mark_id: int):
    try:
        mark = await MarkRepository.get_mark_by_id(mark_id)
        return SMark.model_validate(mark, from_attributes=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/", response_model=SMark)
async def create_mark(mark_data: SMarkCreate):
    try:
        mark = await MarkRepository.create_mark(mark_data)
        return SMark.model_validate(mark, from_attributes=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.put("/update/{mark_id}", response_model=SMark)
async def update_mark(mark_id: int, mark_data: SMarkUpdate, current_user: UserOrm = Depends(get_current_admin)):
    try:
        mark = await MarkRepository.update_mark(mark_id, mark_data)
        return SMark.model_validate(mark, from_attributes=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{mark_id}")
async def delete_mark(mark_id: int, current_user: UserOrm = Depends(get_current_admin)):
    try:
        await MarkRepository.delete_mark(mark_id)
        return {"success": True, "message": f"Марка с id = {mark_id} удалена"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))