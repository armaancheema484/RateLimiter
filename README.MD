\# Redis-Based Token Bucket Rate Limiter



A \*\*multi-server safe\*\* rate limiter built using the \*\*token bucket\*\* algorithm and \*\*Redis Lua scripting\*\* for atomic operations.



This implementation ensures:

\- \*\*Atomicity\*\*: Refill, consume, and persist token state in a single Redis operation.

\- \*\*Consistency\*\*: Uses Redis server time (`TIME`) to ensure multiple application servers share the same time base.

\- \*\*Scalability\*\*: Works across multiple processes and servers without race conditions.



---



\## Features

\- \*\*Token Bucket Algorithm\*\* — Allows bursts up to a maximum capacity.

\- \*\*Multi-Server Safe\*\* — All updates occur in Redis atomically via Lua.

\- \*\*Precise Timing\*\* — Based on Redis' own server clock.

\- \*\*Configurable\*\*:

&nbsp; - `max\_tokens` — Burst capacity.

&nbsp; - `tokens\_per\_second` — Steady refill rate.

&nbsp; - `cost` — Tokens consumed per request.

&nbsp; - `ttl\_seconds` — Key expiration to prevent unbounded growth.



---



\## Requirements

\- Python 3.8+

\- \[redis-py](https://pypi.org/project/redis/) (`pip install redis`)

\- A running Redis instance.



---



\## Installation

```bash

pip install redis



---



\## Usage

from rate\_limiter import RedisRateLimiter



\# Create a limiter for a specific user or endpoint

limiter = RedisRateLimiter(

&nbsp;   redis\_url="redis://localhost:6379/0",

&nbsp;   key="user:123",            # Unique per client/user

&nbsp;   max\_tokens=30,             # Burst capacity

&nbsp;   tokens\_per\_second=10,      # Refill rate

&nbsp;   ttl\_seconds=3600           # Expire keys after 1 hour of inactivity

)



\# Attempt a request

allowed, tokens\_left = limiter.allow\_request(cost=1)

if allowed:

&nbsp;   print(f"Request allowed. {tokens\_left} tokens remaining.")

else:

&nbsp;   print("Request denied. Rate limit exceeded.")



---



\## How It Works

1. Refill Phase

Calculates elapsed time since last request using Redis' TIME command, adds tokens at tokens\_per\_second rate, capped at max\_tokens.



2\. Check Phase

If available tokens ≥ request cost, allow the request and subtract the cost.



3\. Persist Phase

Store updated token count and timestamp in Redis, set TTL for automatic cleanup.



All steps are executed atomically inside Redis using a Lua script, ensuring no race conditions even under heavy load from multiple servers.



