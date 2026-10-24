# Zona VPN — MVP starter

Это стартовый проект, не готовый публичный VPN-сервис. До продаж нужны VPS, секреты, адаптер управления Xray, интеграционные проверки Stars, юридическая проверка и реальные тесты на устройствах.

## Локальный запуск
Python 3.12+, `pip install -r requirements.txt`, скопируйте `.env.example` в `.env`, заполните BOT_TOKEN и ADMIN_IDS, затем `python -m app`.

`VPN_MODE=disabled` по умолчанию: конфигурации не выдаются. Не включайте продажи, пока управление Xray и отзыв доступа не реализованы и не протестированы.

Исходные цены сохранены без изменений: 499 ₽ / 1 месяц, 1 999 ₽ / 2 месяца, 2 999 ₽ / 3 месяца. Цена в Stars задаётся отдельно. Важно: два месячных тарифа стоят 998 ₽, что существенно дешевле тарифа на два месяца.

## Railway test deployment

See [`docs/RAILWAY_TEST_DEPLOY.md`](docs/RAILWAY_TEST_DEPLOY.md). Railway is for testing bot flows only at this stage; VPN access and sales remain disabled.
