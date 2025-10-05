from aiokafka import AIOKafkaProducer
import json
import os




KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
MARK_TOPIC = 'mark_processing'



async def get_producer():
    return AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


async def send_mark_for_processing(mark_id: int, text: str):
    producer = await get_producer()
    await producer.start()
    try:
        message = {
            'mark_id': mark_id,
            'text': text
        }
        await producer.send(MARK_TOPIC, message)
    finally:
        await producer.stop()