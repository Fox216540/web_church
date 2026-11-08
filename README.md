# web_church

## Запуск в Docker

```bash
docker compose up --build -d
```

Сайт доступен по адресам `https://familiadedios.es` и
`https://www.familiadedios.es`. Сервис Caddy автоматически получает и
продлевает TLS-сертификаты Let's Encrypt; вручную создавать или подключать
файлы сертификатов не нужно.

Перед первым запуском убедитесь, что:

- A/AAAA-записи обоих доменов указывают на сервер;
- порты TCP 80 и 443 доступны из интернета и не заняты другим сервисом.
- создана директория `secrets/` с файлами `postgres_password`,
  `django_secret_key`, `bot_token`, `bot_token_help` и `admin_password`;
- у файлов секретов установлены права доступа только для владельца:
  `chmod 700 secrets && chmod 600 secrets/*`.

Секреты не добавляются в `.env` и не попадают в Docker-образ. Docker Compose
монтирует их только тем сервисам, которым они нужны, как read-only файлы в
`/run/secrets`. Заполните `.env` на основе `.env.example` только
несекретными настройками, включая `ADMIN_USER` и `ADMIN_EMAIL`. При миграции
со старой конфигурации удалите из `.env` все пароли, ключи и токены, а сами
секреты перенесите в файлы в `secrets/` и при необходимости отзовите старые
значения.

Проверить выпуск сертификата и состояние прокси можно в логах:

```bash
docker compose logs -f caddy
```

Данные Caddy, включая сертификаты и сведения об их продлении, хранятся в
именованных Docker volumes `caddy_data` и `caddy_config` и сохраняются при
перезапуске контейнера.

## Мониторинг контейнеров

Монитор запускается через systemd на Docker-хосте, а не в контейнере. Он раз в
минуту проверяет сервисы `db`, `web`, `photo`, `support-bot` и `caddy`, и
отправляет одно Telegram-сообщение при остановке, unhealthy-состоянии или
неожиданном рестарте. После восстановления приходит одно сообщение `RECOVERED`.
Повторы одного и того же инцидента не отправляются.

Установка на сервере (выполняется от root):

```bash
install -d -m 755 /usr/local/lib/web-church
install -m 755 scripts/monitor-compose.sh /usr/local/lib/web-church/monitor-compose.sh
install -m 644 deploy/systemd/web-church-monitor.service /etc/systemd/system/
install -m 644 deploy/systemd/web-church-monitor.timer /etc/systemd/system/
install -m 600 deploy/systemd/web-church-monitor.env.example /etc/web-church-monitor.env
```

Отредактируйте `/etc/web-church-monitor.env`: укажите только абсолютный
`PROJECT_DIR`. Монитор безопасно читает числовой `CHAT_ID` из
`${PROJECT_DIR}/.env` и token из `${PROJECT_DIR}/secrets/bot_token`, не
исполняя содержимое `.env`. Затем включите монитор:

```bash
systemctl daemon-reload
systemctl enable --now web-church-monitor.timer
systemctl start web-church-monitor.service
systemctl list-timers web-church-monitor.timer
journalctl -u web-church-monitor.service -f
```

Состояние дедупликации хранится в `/var/lib/web-church-monitor/state.tsv`.
Монитор не перезапускает сервисы: `restart: unless-stopped` в Compose делает
это силами Docker. Docker socket не передаётся контейнерам.

## Зависимости и веб-сервер

Зависимости описаны в `pyproject.toml` и фиксируются в `poetry.lock`.
Локальная установка выполняется командой `poetry install`.

В контейнере Django запускается через Gunicorn. При необходимости его можно
настроить переменными окружения: `PORT` (по умолчанию `8000`),
`GUNICORN_WORKERS` (`3`), `GUNICORN_THREADS` (`2`) и `GUNICORN_TIMEOUT` (`60`).
При старте применяются только существующие миграции; если модели были изменены
без миграции, контейнер завершится с ошибкой до запуска сайта.
