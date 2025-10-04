from database import new_session
from models.mark import MarkOrm
from schemas.mark import SMarkCreate, SMarkUpdate
from sqlalchemy import select, delete




class MarkRepository:
    @classmethod
    async def get_all_marks(cls, limit: int, offset: int) -> list[MarkOrm]:
        async with new_session() as session:
            query = select(MarkOrm).limit(limit).offset(offset)
            result = await session.execute(query)
            return result.scalars().all()


    @classmethod
    async def get_mark_by_id(cls, mark_id: int) -> MarkOrm:
        mark = await cls._get_mark_by_id(mark_id)
        if not mark:
            raise ValueError('Метка не найдена')
        return mark


    @classmethod
    async def _get_mark_by_id(cls, mark_id: int) -> MarkOrm | None:
        async with new_session() as session:
            query = select(MarkOrm).where(MarkOrm.id == mark_id)
            result = await session.execute(query)
            return result.scalars().first()


    @classmethod
    async def create_mark(cls, mark_data: SMarkCreate) -> MarkOrm:
        async with new_session() as session:
            mark = MarkOrm(
                text=mark_data.text,
                tags=mark_data.tags,
                latitude=mark_data.latitude,
                longitude=mark_data.longitude
            )
            session.add(mark)
            await session.flush()
            await session.commit()
            return mark
    

    @classmethod
    async def update_mark(cls, mark_id: int, mark_data: SMarkUpdate) -> MarkOrm:
        mark = await cls.get_mark_by_id(mark_id)
        
        async with new_session() as session:
            mark = await session.merge(mark)
            if mark_data.text is not None:
                mark.text = mark_data.text
            if mark_data.tags is not None:
                mark.tags = mark_data.tags
            if mark_data.latitude is not None:
                mark.latitude = mark_data.latitude
            if mark_data.longitude is not None:
                mark.longitude = mark_data.longitude
            
            await session.commit()
            return mark
    

    @classmethod
    async def delete_mark(cls, mark_id: int):
        mark = await cls.get_mark_by_id(mark_id)
        
        async with new_session() as session:
            await session.delete(mark)
            await session.commit()