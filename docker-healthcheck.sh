#!/bin/bash
# ARES Health Check Script for Docker containers

set -e

# Check if the application is running on the expected port
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✓ HTTP health check: PASSED"
else
    echo "✗ HTTP health check: FAILED"
    exit 1
fi

# Check database connectivity (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    if timeout 5 python -c "
import asyncio
import asyncpg
import os
from urllib.parse import urlparse

async def check_db():
    try:
        url = urlparse(os.getenv('DATABASE_URL'))
        conn = await asyncpg.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]
        )
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception as e:
        print(f'Database check failed: {e}')
        return False

result = asyncio.run(check_db())
exit(0 if result else 1)
" 2>/dev/null; then
        echo "✓ Database connectivity: PASSED"
    else
        echo "✗ Database connectivity: FAILED"
        exit 1
    fi
fi

# Check Redis connectivity (if REDIS_URL is set)
if [ -n "$REDIS_URL" ]; then
    if timeout 5 python -c "
import redis
import os
from urllib.parse import urlparse

try:
    url = urlparse(os.getenv('REDIS_URL'))
    r = redis.Redis(host=url.hostname, port=url.port, db=0)
    r.ping()
    print('Redis connectivity: PASSED')
except Exception as e:
    print(f'Redis check failed: {e}')
    exit(1)
" 2>/dev/null; then
        echo "✓ Redis connectivity: PASSED"
    else
        echo "✗ Redis connectivity: FAILED"
        exit 1
    fi
fi

echo "✓ All health checks passed!"
exit 0