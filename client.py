
import asyncio
import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"
TOTAL_REQUESTS = 25
TEST_CASES = [10, 25]


async def send_request(client, request_id):
    response = await client.get(
        f"{BASE_URL}/test",
        params={"request_id": request_id}
    )
    response.raise_for_status()
    return response.json()


async def run_testcase(client, testcase_id, max_tokens):
    # Configure the server's thread-pool capacity
    response = await client.post(
        f"{BASE_URL}/configure",
        json={"max_tokens": max_tokens}
    )
    response.raise_for_status()

    print(f"\nTestcase {testcase_id}: max_tokens={max_tokens}")

    # Start timing before dispatching requests
    start_time = time.perf_counter()

    # Send all requests concurrently
    tasks = [
        send_request(client, i)
        for i in range(1, TOTAL_REQUESTS + 1)
    ]

    results = await asyncio.gather(*tasks)

    # Measure total time for all requests
    total_time = time.perf_counter() - start_time

    return {
        "testcaseid": testcase_id,
        "max_tokens": max_tokens,
        "no. of requests": TOTAL_REQUESTS,
        "thread execution stats": sorted(
            results,
            key=lambda x: x["request_id"]
        ),
        "total_execution_time": round(total_time, 3)
    }


async def main():
    all_results = []

    async with httpx.AsyncClient(timeout=60) as client:
        for testcase_id, max_tokens in enumerate(TEST_CASES, 1):
            result = await run_testcase(
                client,
                testcase_id,
                max_tokens
            )

            all_results.append(result)

            print(
                f"Completed in "
                f"{result['total_execution_time']} seconds"
            )

    # Save results as JSON
    with open("load_testing/load_test_results.json", "w") as f:
        json.dump(all_results, f, indent=4)

    print("\nResults saved to load_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
