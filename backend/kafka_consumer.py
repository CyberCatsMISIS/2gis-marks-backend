import asyncio
import json
import httpx
from aiokafka import AIOKafkaConsumer
from database import new_session
from models.mark import MarkOrm
import os




KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
MARK_TOPIC = 'mark_processing'

async def consume_marks():
    consumer = AIOKafkaConsumer(
        MARK_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="mark_processor_group",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            mark_data = msg.value
            await process_mark(mark_data)
    finally:
        await consumer.stop()

async def process_mark(mark_data: dict):
    mark_id = mark_data['mark_id']
    text = mark_data['text']
    
    # Получаем теги от classifier
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://classifier:3002/parse",
                json={"text": text},
                timeout=30.0
            )
            response.raise_for_status()
            tags_data = response.json()
            parsed_tags = tags_data.get("tags", [])
    except Exception as e:
        print(f"Error getting tags for mark {mark_id}: {e}")
        parsed_tags = []
    
    # Обновляем метку в БД
    async with new_session() as session:
        mark = await session.get(MarkOrm, mark_id)
        if mark:
            mark.tags = parsed_tags
            await session.commit()
            print(f"Updated mark {mark_id} with tags: {parsed_tags}")