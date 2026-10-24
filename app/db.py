import os, aiosqlite
from datetime import datetime, timezone
SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orders(
 id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, plan TEXT NOT NULL,
 stars INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
 created TEXT NOT NULL, charge_id TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS subscriptions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, plan TEXT NOT NULL,
 starts TEXT NOT NULL, expires TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notifications(
 id INTEGER PRIMARY KEY AUTOINCREMENT, subscription_id INTEGER NOT NULL,
 kind TEXT NOT NULL, sent TEXT NOT NULL, UNIQUE(subscription_id,kind)
);
CREATE TABLE IF NOT EXISTS audit(
 id INTEGER PRIMARY KEY AUTOINCREMENT, actor INTEGER, action TEXT NOT NULL,
 target TEXT, created TEXT NOT NULL
);
'''
def now(): return datetime.now(timezone.utc)
class Database:
 def __init__(self,path): self.path=path
 async def connect(self):
  os.makedirs(os.path.dirname(os.path.abspath(self.path)),exist_ok=True)
  db=await aiosqlite.connect(self.path); db.row_factory=aiosqlite.Row; return db
 async def init(self):
  async with await self.connect() as db: await db.executescript(SCHEMA); await db.commit()
 async def register(self,uid):
  async with await self.connect() as db:
   await db.execute("INSERT OR IGNORE INTO users VALUES(?,?)",(uid,now().isoformat())); await db.commit()
 async def order(self,oid,uid,plan,stars):
  async with await self.connect() as db:
   await db.execute("INSERT INTO orders(id,user_id,plan,stars,created) VALUES(?,?,?,?,?)",(oid,uid,plan,stars,now().isoformat())); await db.commit()
 async def get_order(self,oid):
  async with await self.connect() as db: return await (await db.execute("SELECT * FROM orders WHERE id=?",(oid,))).fetchone()
 async def paid(self,oid,uid,currency,amount,charge):
  async with await self.connect() as db:
   await db.execute("BEGIN IMMEDIATE")
   row=await (await db.execute("SELECT * FROM orders WHERE id=?",(oid,))).fetchone()
   if not row or row["user_id"]!=uid or row["status"]!="pending" or currency!="XTR" or amount!=row["stars"]:
    await db.rollback(); return None
   try: await db.execute("UPDATE orders SET status='paid',charge_id=? WHERE id=?",(charge,oid))
   except aiosqlite.IntegrityError: await db.rollback(); return None
   await db.commit(); return row["plan"]
 async def activate(self,uid,plan,months):
  import calendar
  current=now()
  async with await self.connect() as db:
   row=await (await db.execute("SELECT expires FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires DESC LIMIT 1",(uid,))).fetchone()
   start=current
   if row:
    old=datetime.fromisoformat(row["expires"])
    if old>current: start=old
   m=start.month-1+months; year=start.year+m//12; month=m%12+1
   day=min(start.day,calendar.monthrange(year,month)[1])
   end=start.replace(year=year,month=month,day=day)
   await db.execute("UPDATE subscriptions SET status='expired' WHERE user_id=? AND status='active'",(uid,))
   await db.execute("INSERT INTO subscriptions(user_id,plan,starts,expires,status) VALUES(?,?,?,?,?)",(uid,plan,start.isoformat(),end.isoformat(),"active"))
   await db.commit(); return end
 async def subscription(self,uid):
  async with await self.connect() as db:
   row=await (await db.execute("SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires DESC LIMIT 1",(uid,))).fetchone()
   if row and datetime.fromisoformat(row["expires"])<=now():
    await db.execute("UPDATE subscriptions SET status='expired' WHERE id=?",(row["id"],)); await db.commit(); return None
   return row
 async def active_rows(self):
  async with await self.connect() as db: return await (await db.execute("SELECT * FROM subscriptions WHERE status='active'")).fetchall()
 async def has_notice(self,sid,kind):
  async with await self.connect() as db:
   row=await (await db.execute("SELECT 1 FROM notifications WHERE subscription_id=? AND kind=?",(sid,kind))).fetchone()
   return row is not None
 async def mark_notice(self,sid,kind):
  async with await self.connect() as db:
   try:
    await db.execute("INSERT INTO notifications(subscription_id,kind,sent) VALUES(?,?,?)",(sid,kind,now().isoformat()))
    await db.commit()
    return True
   except aiosqlite.IntegrityError:
    return False
 async def expire_subscription(self,sid):
  async with await self.connect() as db:
   await db.execute("UPDATE subscriptions SET status='expired' WHERE id=? AND status='active'",(sid,))
   await db.commit()
 async def stats(self):
  async with await self.connect() as db:
   a=await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
   b=await (await db.execute("SELECT COUNT(*) FROM subscriptions WHERE status='active'")).fetchone()
   c=await (await db.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")).fetchone()
   return a[0],b[0],c[0]
