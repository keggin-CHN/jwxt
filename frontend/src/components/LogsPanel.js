import React, { useState } from 'react';
import axios from 'axios';
import './LogsPanel.css';

function LogsPanel({ logs, onRefresh }) {
  const [isClearing, setIsClearing] = useState(false);

  const getLogIcon = (level) => {
    switch(level) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  const getLogClass = (level) => {
    return `log-item log-${level}`;
  };

  const handleClearLogs = async () => {
    if (!window.confirm('确定要清空所有日志吗？')) {
      return;
    }

    setIsClearing(true);
    try {
      const response = await axios.post('/api/logs/clear');
      if (response.data.success) {
        alert('日志已清空');
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      alert('清空日志失败：' + error.message);
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="logs-panel">
      <div className="panel-header">
        <div>
          <h2>📝 运行日志</h2>
          <p className="log-count">共 {logs.length} 条记录</p>
        </div>
        <button 
          onClick={handleClearLogs} 
          disabled={isClearing || logs.length === 0}
          className="clear-logs-btn"
        >
          {isClearing ? '清空中...' : '🗑️ 清空日志'}
        </button>
      </div>

      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="no-logs">
            <p>暂无日志记录</p>
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className={getLogClass(log.level)}>
              <div className="log-icon">{getLogIcon(log.level)}</div>
              <div className="log-content">
                <div className="log-message">{log.message}</div>
                <div className="log-time">{log.time}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default LogsPanel;
