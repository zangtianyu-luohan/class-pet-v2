import asyncio
from datetime import datetime
from typing import Any


class SSEManager:
    """SSE 连接管理器"""

    def __init__(self):
        self.connections: list[asyncio.Queue] = []

    async def connect(self) -> asyncio.Queue:
        """创建新的 SSE 连接"""
        queue = asyncio.Queue()
        self.connections.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue):
        """断开 SSE 连接"""
        if queue in self.connections:
            self.connections.remove(queue)

    async def broadcast(self, event_type: str, data: dict[str, Any]):
        """广播事件到所有连接"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for queue in self.connections:
            await queue.put(event)


# 全局 SSE 管理器实例
sse_manager = SSEManager()
