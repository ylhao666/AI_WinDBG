"""WebSocket 连接管理器"""

from typing import List, Set, Dict, Any
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
import json
import asyncio

from src.core.logger import LoggerManager


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        """初始化 WebSocket 管理器"""
        self.output_connections: Set[WebSocket] = set()
        self.session_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect_output(self, websocket: WebSocket):
        """连接输出 WebSocket"""
        await websocket.accept()
        async with self._lock:
            self.output_connections.add(websocket)
        LoggerManager.info(f"输出 WebSocket 连接建立: {websocket.client}")
    
    async def disconnect_output(self, websocket: WebSocket):
        """断开输出 WebSocket"""
        async with self._lock:
            self.output_connections.discard(websocket)
        LoggerManager.info(f"输出 WebSocket 连接断开: {websocket.client}")
    
    async def connect_session(self, websocket: WebSocket):
        """连接会话 WebSocket"""
        await websocket.accept()
        async with self._lock:
            self.session_connections.add(websocket)
        LoggerManager.info(f"会话 WebSocket 连接建立: {websocket.client}")
    
    async def disconnect_session(self, websocket: WebSocket):
        """断开会话 WebSocket"""
        async with self._lock:
            self.session_connections.discard(websocket)
        LoggerManager.info(f"会话 WebSocket 连接断开: {websocket.client}")
    
    async def broadcast_output(self, message: Dict[str, Any]):
        """广播输出消息"""
        if not self.output_connections:
            return
        
        disconnected = set()
        async with self._lock:
            for connection in self.output_connections:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_json(message)
                    else:
                        disconnected.add(connection)
                except Exception as e:
                    LoggerManager.error(f"发送输出消息失败: {str(e)}")
                    disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect_output(connection)
    
    async def broadcast_session_update(self, message: Dict[str, Any]):
        """广播会话更新消息"""
        if not self.session_connections:
            return
        
        disconnected = set()
        async with self._lock:
            for connection in self.session_connections:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_json(message)
                    else:
                        disconnected.add(connection)
                except Exception as e:
                    LoggerManager.error(f"发送会话消息失败: {str(e)}")
                    disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect_session(connection)
    
    async def send_to_output(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送消息到特定输出连接"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            LoggerManager.error(f"发送消息失败: {str(e)}")
            self.disconnect_output(websocket)
    
    async def send_to_session(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送消息到特定会话连接"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            LoggerManager.error(f"发送消息失败: {str(e)}")
            self.disconnect_session(websocket)
    
    async def disconnect_all(self):
        """断开所有连接"""
        async with self._lock:
            self.output_connections.clear()
            self.session_connections.clear()
        LoggerManager.info("所有 WebSocket 连接已断开")
    
    def get_connection_count(self) -> Dict[str, int]:
        """获取连接数量"""
        return {
            "output": len(self.output_connections),
            "session": len(self.session_connections)
        }
