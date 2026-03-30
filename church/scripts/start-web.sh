#!/usr/bin/env sh
set -eu

if python manage.py makemigrations --check --dry-run --noinput >/dev/null 2>&1; then
  echo "No model changes, skip makemigrations"
else
  echo "Model changes detected, running makemigrations"
  python manage.py makemigrations --noinput
fi

python manage.py migrate --noinput
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User=get_user_model(); u=os.environ.get('ADMIN_USER'); e=os.environ.get('ADMIN_EMAIL'); p=os.environ.get('ADMIN_PASSWORD'); User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p)"
python manage.py collectstatic --noinput

exec python manage.py runserver 0.0.0.0:8000
