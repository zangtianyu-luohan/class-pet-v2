// frontend/src/api/sse.js

class SSEClient {
  constructor() {
    this.eventSource = null
    this.listeners = {}
    this.reconnectTimer = null
    this.isConnecting = false
  }

  connect() {
    if (this.isConnecting || (this.eventSource && this.eventSource.readyState === EventSource.OPEN)) {
      return
    }

    this.isConnecting = true
    this.eventSource = new EventSource('/api/sse/events')

    this.eventSource.onopen = () => {
      this.isConnecting = false
      console.log('SSE 连接已建立')
    }

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data.data)
      } catch (e) {
        console.error('SSE 数据解析失败:', e)
      }
    }

    this.eventSource.onerror = () => {
      this.isConnecting = false
      console.log('SSE 连接断开，3秒后重连...')
      this.eventSource.close()

      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
      }

      this.reconnectTimer = setTimeout(() => {
        this.connect()
      }, 3000)
    }
  }

  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = []
    }
    this.listeners[eventType].push(callback)
  }

  off(eventType, callback) {
    if (this.listeners[eventType]) {
      this.listeners[eventType] = this.listeners[eventType].filter(cb => cb !== callback)
    }
  }

  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach(callback => callback(data))
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }

    this.isConnecting = false
  }
}

export const sseClient = new SSEClient()
