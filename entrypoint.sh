#!/bin/sh
echo "Waiting for postgres..."
until python -c "
import asyncio, asyncpg, os
async def check():
    await asyncpg.connect(os.environ['DATABASE_URL'].replace('postgresql+asyncpg', 'postgresql'))
asyncio.run(check())
" 2>/dev/null; do
  echo "Postgres not ready, retrying in 1s..."
  sleep 1
done

echo "Running migrations..."
# If no versions exist yet, autogenerate
if [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
  echo "No migrations found, generating..."
  alembic revision --autogenerate -m "init"
fi
alembic upgrade head

echo "Starting server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8002
