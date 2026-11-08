#!/usr/bin/env sh
set -eu

if ! python manage.py makemigrations --check --dry-run --noinput; then
  echo "Model changes without migrations detected. Create and commit migrations before deployment." >&2
  exit 1
fi

python manage.py migrate --noinput
python manage.py shell -c "from config import require_env; from django.contrib.auth import get_user_model; User=get_user_model(); u=require_env('ADMIN_USER'); e=require_env('ADMIN_EMAIL'); p=require_env('ADMIN_PASSWORD'); User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p)"
python manage.py collectstatic --noinput

exec gunicorn church.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
