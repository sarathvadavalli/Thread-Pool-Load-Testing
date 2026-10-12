# FastAPI worker-thread load test

## Task

Measure how the AnyIO worker-thread pool limit affects a FastAPI endpoint
when several requests arrive concurrently. The `/test` endpoint is `async`,
but delegates its blocking work to a worker thread with
`anyio.to_thread.run_sync`. Each request simulates two seconds of blocking
work and reports its request ID, worker thread ID, time waiting for a worker,
execution time, and total elapsed time.

The `/configure` endpoint changes the process-wide AnyIO thread limiter for
the next test case. It accepts JSON such as `{"max_tokens": 10}`.

## Run the test

From the repository root, start the server:

```powershell
uvicorn load_testing.server:app --host 127.0.0.1 --port 8000
```

In another terminal, run the asynchronous client:

```powershell
python load_testing/client.py
```

The client uses `asyncio.gather` to issue all 25 requests concurrently for
each test case. It runs the two configured pool limits (`10` and `25`)
sequentially, prints each case's total elapsed time, and writes per-request
measurements to `load_testing/load_test_results.json`. Change
`TOTAL_REQUESTS` or `TEST_CASES` in `client.py` to try different loads and
pool limits.

## Observed results

The checked-in results file records these runs:

| Worker-pool limit | Concurrent requests | Total elapsed | Average worker wait | Maximum worker wait | Average execution |
|---:|---:|---:|---:|---:|---:|
| 10 | 25 | 6.095 s | 1.601 s | 4.004 s | 2.011 s |
| 25 | 25 | 2.170 s | 0.002 s | 0.004 s | 2.010 s |

Each worker execution took about two seconds, as expected from the simulated
blocking workload. The run with 10 worker tokens needed multiple waves of
work; the run with 25 tokens could start all 25 requests without meaningful
worker-pool queueing. The recorded thread IDs also show 10 distinct workers
in the first run and 25 in the second.

## Outcomes and interpretation

For this I/O-style blocking workload and this request volume, increasing the
worker limit from 10 to 25 reduced total elapsed time from about 6.1 seconds
to 2.2 seconds by allowing more work to overlap. The wait-time measurements
show the queueing effect directly. Raising the limit does not make each
request's blocking operation faster; it lets more of those operations run
at once.

This is a controlled local experiment, not a universal capacity target.
Higher worker counts also increase simultaneous resource use, and benefits
can level off or reverse if the actual workload, upstream service, or host
cannot sustain the additional concurrency. Repeat runs under the intended
deployment conditions before choosing a production pool size.

## Additional visualizations

[View Thread Pool Analysis](./visualization.ipynb)