import asyncio
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.background.paper_tasks import _concurrency_limit

async def mock_task(i):
    print(f"Task {i} waiting for semaphore...")
    async with _concurrency_limit:
        print(f"Task {i} acquired semaphore! Running...")
        await asyncio.sleep(1) # Simulate work
        print(f"Task {i} released semaphore.")

async def main():
    print("Starting concurrency test...")
    # Python 3.10+ semaphore doesn't expose value easily, but we know it's 3
    
    tasks = [mock_task(i) for i in range(10)]
    start = time.time()
    await asyncio.gather(*tasks)
    end = time.time()
    
    print(f"Total time: {end - start:.2f}s")
    # 10 tasks, 3 at a time, each 1s.
    # Batch 1: 0,1,2 (1s)
    # Batch 2: 3,4,5 (1s)
    # Batch 3: 6,7,8 (1s)
    # Batch 4: 9 (1s)
    # Total should be around 4s. If it was parallel, it would be 1s.
    
    if 3.5 < (end - start) < 4.5:
        print("SUCCESS: Concurrency limited correctly.")
    else:
        print(f"FAILURE: Timing mismatch. Expected ~4s for 10 tasks with limit 3.")

if __name__ == "__main__":
    asyncio.run(main())
