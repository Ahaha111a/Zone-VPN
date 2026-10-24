"""Durable-ish subscription notification worker.

Notifications are recorded only after Telegram accepts the message. This avoids
silently losing reminders when Telegram is temporarily unavailable. A crash
between send and record can still cause a duplicate; Telegram Bot API does not
provide idempotency keys for sendMessage.
"""
import asyncio
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)
REMINDERS = ((3, "d3"), (2, "d2"), (1, "d1"))

async def expiry_worker(bot, db, interval_seconds: int = 3600):
    while True:
        try:
            for row in await db.active_rows():
                try:
                    end = datetime.fromisoformat(row["expires"])
                    if end.tzinfo is None:
                        end = end.replace(tzinfo=timezone.utc)
                    days_left = (end - datetime.now(timezone.utc)).total_seconds() / 86400

                    if days_left <= 0:
                        if not await db.has_notice(row["id"], "expired"):
                            try:
                                await bot.send_message(row["user_id"], "Срок подписки Zona VPN закончился. Продлите подписку, чтобы восстановить доступ.")
                            except Exception:
                                log.warning("Не удалось отправить уведомление об окончании user_id=%s", row["user_id"], exc_info=True)
                            else:
                                await db.mark_notice(row["id"], "expired")
                        await db.expire_subscription(row["id"])
                        continue

                    # Send only the nearest applicable reminder. This also
                    # recovers after downtime without sending 3 reminders at once.
                    due = next(((n, kind) for n, kind in reversed(REMINDERS) if days_left <= n), None)
                    if due:
                        n, kind = due
                        if not await db.has_notice(row["id"], kind):
                            try:
                                await bot.send_message(row["user_id"], f"Напоминание: подписка Zona VPN закончится примерно через {n} дн.")
                            except Exception:
                                log.warning("Не удалось отправить уведомление user_id=%s", row["user_id"], exc_info=True)
                            else:
                                await db.mark_notice(row["id"], kind)
                except Exception:
                    log.exception("Ошибка обработки подписки id=%s", row["id"])
        except Exception:
            log.exception("Ошибка планировщика подписок")
        await asyncio.sleep(interval_seconds)
