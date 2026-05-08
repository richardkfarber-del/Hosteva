import asyncio
import os
import json
import logging
from uuid import uuid4

class RedisMock:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue(self, task_name, payload):
        await self.queue.put({"task": task_name, "payload": payload, "id": str(uuid4())})

    async def dequeue(self):
        return await self.queue.get()

class S3Mock:
    def __init__(self, bucket="hosteva-documents"):
        self.bucket = bucket

    async def upload_document(self, file_content, file_name, tenant_id="default_tenant", property_id="default_property"):
        await asyncio.sleep(0.5)
        structural_prefix = f"{tenant_id}/{property_id}/{file_name}"
        return f"s3://{self.bucket}/{structural_prefix}"

redis_client = RedisMock()
s3_client = S3Mock()

async def process_document_generation(payload):
    property_id = payload.get('property_id', 'default_property')
    tenant_id = payload.get('tenant_id', 'default_tenant')
    logging.info(f"Generating document for property: {property_id}")
    await asyncio.sleep(2)
    
    file_name = f"doc_{property_id}.pdf"
    file_url = await s3_client.upload_document(
        b"PDF_CONTENT", 
        file_name,
        tenant_id=tenant_id,
        property_id=property_id
    )
    logging.info(f"Document uploaded to: {file_url}")
    return file_url

async def worker_main():
    logging.info("Starting Redis background worker...")
    while True:
        task = await redis_client.dequeue()
        if task['task'] == 'generate_document':
            asyncio.create_task(process_document_generation(task['payload']))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(worker_main())
