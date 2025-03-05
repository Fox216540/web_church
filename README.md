# web_church
## Команды для запуска на контейнере
1. ```bash
   docker-compose build
2. ```bash
   docker-compose up -d
3. ```bash
    docker exec -it church_web_1 bash
4. ```bash
    python manage.py migrate
5. ```bash
    python manage.py createsuperuser
6. ```bash
    docker exec -it church-db bash
7. ```bash
    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /dump/"$DUMP_NAME"