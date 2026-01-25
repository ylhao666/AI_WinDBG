import { WebSocketMessage, AnalysisProgress, AnalysisThinking } from '../types';

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect(url: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        const { type, ...data } = message;
        this.emit(type, data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(url), this.reconnectDelay);
      }
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((callback) => callback(data));
    }
  }

  onAnalysisProgress(callback: (data: AnalysisProgress) => void) {
    this.on('analysis_progress', callback);
  }

  offAnalysisProgress(callback: (data: AnalysisProgress) => void) {
    this.off('analysis_progress', callback);
  }

  onAnalysisThinking(callback: (data: AnalysisThinking) => void) {
    this.on('analysis_thinking', callback);
  }

  offAnalysisThinking(callback: (data: AnalysisThinking) => void) {
    this.off('analysis_thinking', callback);
  }

  onAnalysisReport(callback: (data: { report: any }) => void) {
    this.on('analysis_report', callback);
  }

  offAnalysisReport(callback: (data: { report: any }) => void) {
    this.off('analysis_report', callback);
  }

  onCommandOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.on('command_output', callback);
  }

  offCommandOutput(callback: (data: { output: string; command: string; mode: string }) => void) {
    this.off('command_output', callback);
  }

  onSessionLoaded(callback: () => void) {
    this.on('session_loaded', callback);
  }

  offSessionLoaded(callback: () => void) {
    this.off('session_loaded', callback);
  }

  onSessionClosed(callback: () => void) {
    this.on('session_closed', callback);
  }

  offSessionClosed(callback: () => void) {
    this.off('session_closed', callback);
  }
}

export const wsManager = new WebSocketManager();
