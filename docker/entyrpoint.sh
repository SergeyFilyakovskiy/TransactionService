#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."

python -c "
import time, socket
for i in range(30):
    try:
        s = socket.create_connection(('postgres', 5432), timeout=2)
        s.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit('PostgreSQL don't start in 30 sec')
"
echo "PostgreSQL is up"

echo "Applying migrations..."
alembic upgrade head
echo "Migrations applied"

echo "Starting application..."
exec "$@"
