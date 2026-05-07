#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Run migrations only when explicitly requested for an existing production database.
if [ "${RUN_MIGRATIONS:-False}" = "True" ]; then
	python manage.py migrate
fi

# Keep seeding optional to avoid modifying existing production databases.
if [ "${RUN_SEED_DATA:-False}" = "True" ]; then
	python manage.py seed_governorates
	python manage.py seed_items
fi
