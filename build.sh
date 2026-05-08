#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Always run migrations (safe - only applies unapplied migrations).
python manage.py migrate

# Always seed reference data (safe - uses update_or_create, no duplicates).
python manage.py seed_governorates
python manage.py seed_items
