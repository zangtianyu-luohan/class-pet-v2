# backend/app/routes/sse.py

import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..utils.sse_manager import sse_manager

router = APIRouter()


@router.get("/api/sse/events")
async def sse_events(request: Request):
    """SSE 事件流端点"""

    async def event_generator():
        # 创建连接
        queue = await sse_manager.connect()
        try:
            while True:
                # 检查客户端是否断开
                if await request.is_disconnected():
                    break

                # 获取事件
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': ''}, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.disconnect(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
