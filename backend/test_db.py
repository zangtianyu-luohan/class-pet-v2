import asyncio
import traceback
from app.database import engine, Base
from app.models import *

async def test():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('Tables created OK')

        from app.utils.auth import hash_password
        print('Hash test:', hash_password('test123')[:20])
        print('All good!')
    except Exception as e:
        traceback.print_exc()
    finally:
        await engine.dispose()

asyncio.run(test())
