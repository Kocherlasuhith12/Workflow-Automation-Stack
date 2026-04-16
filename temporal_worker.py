import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import MyWorkflow
from activities import call_restate_activity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("⏳ Connecting to Temporal at temporal:7233 ...")

    # Retry loop — wait for Temporal to be ready on startup
    for attempt in range(10):
        try:
            client = await Client.connect("temporal:7233")
            logger.info("✅ Connected to Temporal!")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/10 failed: {e}. Retrying in 3s...")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("❌ Could not connect to Temporal after 10 attempts.")

    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[MyWorkflow],
        activities=[call_restate_activity],
    )

    logger.info("🚀 Worker started. Listening on task queue: my-task-queue")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())