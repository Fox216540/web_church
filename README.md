# web_church
## Команды для запуска на контейнере
```docker-compose build```

```docker-compose up -d```

```docker exec -it church_web_1 bash```

```python manage.py migrate```

```python manage.py createsuperuser```

```docker exec -it church-db bash```

```pg_restore -U root -d "$POSTGRES_DB" /dump/"$DUMP_NAME"```