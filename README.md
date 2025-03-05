# web_church
## Быстрые команды для запуска на контейнере
1. ```bash
   docker-compose up --build -d db
2. ```bash
   docker exec church-db bash -c "pg_restore -U \$POSTGRES_USER -d \$POSTGRES_DB /dump/\$DUMP_NAME"
3. ```bash
    docker-compose up --build web
