import httpx
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
        # В Docker используем имя сервиса вместо localhost
        tag_service_url = "http://classifier:3002/parse"  # Или другое имя контейнера
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    tag_service_url,
                    json={"text": mark_data.text},
                    timeout=10.0
                )
                response.raise_for_status()
                
                tags_data = response.json()
                parsed_tags = tags_data.get("tags", [])
                
        except httpx.RequestError as e:
            # Если сервис недоступен, используем дефолтные теги
            parsed_tags = mark_data.tags
            print(f"Tag service unavailable: {e}")
        except httpx.HTTPStatusError as e:
            parsed_tags = mark_data.tags
            print(f"Tag service error: {e}")
        except Exception as e:
            # На всякий случай ловим все остальные исключения
            parsed_tags = mark_data.tags
            print(f"Unexpected error: {e}")
        
        # Создаем метку с полученными тегами
        async with new_session() as session:
            mark = MarkOrm(
                text=mark_data.text,
                tags=parsed_tags,
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
            
            # Обновляем только переданные поля
            update_data = mark_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(mark, field, value)
                
            await session.commit()
            return mark
        

    @classmethod
    async def delete_mark(cls, mark_id: int):
        mark = await cls.get_mark_by_id(mark_id)
        
        async with new_session() as session:
            await session.delete(mark)
            await session.commit()