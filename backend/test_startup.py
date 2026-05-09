import asyncio
from app.database import engine, Base
from app.models import *

async def test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tables created")
    await engine.dispose()

asyncio.run(test())
