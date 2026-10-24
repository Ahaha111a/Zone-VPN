import os, uuid
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from config import settings, PLANS
router=Router()
def menu():
 return InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="🔌 Подключить VPN",callback_data="connect"),InlineKeyboardButton(text="💳 Купить",callback_data="plans")],
  [InlineKeyboardButton(text="📄 Моя подписка",callback_data="sub"),InlineKeyboardButton(text="🔄 Продлить",callback_data="plans")],
  [InlineKeyboardButton(text="📘 Инструкция",callback_data="helpinfo"),InlineKeyboardButton(text="🆘 Поддержка",callback_data="support")],
  [InlineKeyboardButton(text="Условия",callback_data="terms")]])
def planmenu():
 return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{p.title} — {p.price_rub} ₽",callback_data="buy:"+p.code)] for p in PLANS.values()])
@router.message(CommandStart())
async def start(m:Message,db):
 await db.register(m.from_user.id)
 await m.answer("Добро пожаловать в Zona VPN. Пробного периода нет. Выберите действие:",reply_markup=menu())
@router.message(Command("help"))
async def help_cmd(m): await m.answer("Команды: /plans /subscription /connect /renew /support /terms /paysupport")
@router.message(Command("plans"))
@router.message(Command("renew"))
async def plans(m): await m.answer("Выберите тариф:",reply_markup=planmenu())
@router.message(Command("subscription"))
async def sub(m,db):
 r=await db.subscription(m.from_user.id)
 await m.answer(f"Активна до {r['expires']} UTC" if r else "Активной подписки нет.")
@router.message(Command("connect"))
async def connect(m,db):
 r=await db.subscription(m.from_user.id)
 await m.answer("VPN-адаптер ещё не настроен; конфигурация не выдана." if r else "Для подключения нужна активная подписка.")
@router.message(Command("support"))
@router.message(Command("paysupport"))
async def support(m): await m.answer(("Поддержка: @"+settings.support) if settings.support else "Поддержка пока не настроена.")
@router.message(Command("terms"))
async def terms(m): await m.answer(settings.terms_url or "Условия обслуживания нужно опубликовать до продаж.")
@router.callback_query(F.data=="plans")
async def cbplans(c): await c.message.answer("Выберите тариф:",reply_markup=planmenu()); await c.answer()
@router.callback_query(F.data.startswith("buy:"))
async def buy(c,db):
 code=c.data.split(":",1)[1]; p=PLANS.get(code)
 stars=os.getenv(p.stars_env,"") if p else ""
 if not p: await c.answer("Неизвестный тариф",show_alert=True); return
 # Fail closed: never collect money until both payment handling and actual VPN delivery are implemented and verified.
 if not settings.sales_enabled or not settings.payment_delivery_ready or settings.vpn_mode != "xray":
  await c.message.answer("Продажи временно закрыты: автоматическая выдача и отзыв VPN-доступа ещё не прошли проверку. Оплата не списывается. Следите за сообщением о запуске.")
  await c.answer(); return
 if not stars.isdigit() or int(stars)<=0:
  await c.message.answer(f"{p.title}: {p.price_rub} ₽. Оплата Stars не включена: задайте отдельную подтверждённую цену в Stars.")
  await c.answer(); return
 oid=uuid.uuid4().hex; await db.register(c.from_user.id); await db.order(oid,c.from_user.id,code,int(stars))
 await c.message.answer_invoice(title="Zona VPN — "+p.title,description="Цифровая VPN-подписка",payload=oid,currency="XTR",prices=[LabeledPrice(label=p.title,amount=int(stars))],provider_token="")
 await c.answer()
@router.pre_checkout_query()
async def checkout(q,db):
 o=await db.get_order(q.invoice_payload)
 ok=bool(o and o["status"]=="pending" and o["user_id"]==q.from_user.id and q.currency=="XTR" and q.total_amount==o["stars"])
 await q.answer(ok=ok,error_message=None if ok else "Заказ или сумма не совпадают.")
@router.message(F.successful_payment)
async def success(m,db):
 p=m.successful_payment
 code=await db.paid(p.invoice_payload,m.from_user.id,p.currency,p.total_amount,p.telegram_payment_charge_id)
 if not code: await m.answer("Платёж не удалось сопоставить с ожидающим заказом. Обратитесь в поддержку."); return
 await m.answer("Платёж подтверждён. Выдача доступа ожидает настройки и проверки VPN-сервера; обратитесь в поддержку.")
@router.callback_query(F.data=="sub")
async def cbsub(c,db):
 r=await db.subscription(c.from_user.id); await c.message.answer(f"Активна до {r['expires']} UTC" if r else "Активной подписки нет."); await c.answer()
@router.callback_query(F.data=="connect")
async def cbconnect(c): await c.message.answer("Выдача конфигурации заблокирована до настройки VPN-адаптера."); await c.answer()
@router.callback_query(F.data=="helpinfo")
async def helpinfo(c): await c.message.answer("Установите HAPP или v2rayTun из официального магазина. Импорт по ссылке/QR будет доступен после настройки сервера."); await c.answer()
@router.callback_query(F.data=="support")
async def cbsupport(c): await c.message.answer(("Поддержка: @"+settings.support) if settings.support else "Поддержка не настроена."); await c.answer()
@router.callback_query(F.data=="terms")
async def cbterms(c): await c.message.answer(settings.terms_url or "Условия ещё не опубликованы."); await c.answer()
@router.message(Command("admin"))
async def admin(m,db):
 if m.from_user.id not in settings.admins: await m.answer("Недостаточно прав."); return
 u,s,p=await db.stats(); await m.answer(f"Админ-статистика\nПользователей: {u}\nАктивных подписок: {s}\nОжидающих заказов: {p}")
