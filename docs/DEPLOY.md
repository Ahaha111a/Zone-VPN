# Развёртывание (Ubuntu LTS)

1. Установите Python 3.12+, git и создайте пользователя службы.
2. Поместите проект в `/opt/zona-vpn`.
3. Создайте venv и установите `requirements.txt`.
4. Скопируйте `.env.example` в `/etc/zona-vpn/zona-vpn.env`, права файла 600.
5. Укажите `BOT_TOKEN`, `ADMIN_IDS`, `DATABASE_PATH=/var/lib/zona-vpn/zona.sqlite3`.
6. Установите `deploy/zona-vpn.service` в `/etc/systemd/system/`, выполните `systemctl daemon-reload`, `systemctl enable --now zona-vpn`.
7. Проверьте `systemctl status zona-vpn` и `journalctl -u zona-vpn`.

Не включайте продажи: адаптер Xray, отзыв клиентов, обработка возвратов и надёжные повторные уведомления требуют доработки и тестов. Не коммитьте `.env`. Настройте SSH-ключи, firewall, обновления и внешнюю резервную копию; обязательно проверьте восстановление.
