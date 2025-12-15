import React from 'react';
import './LogsPanel.css';

function LogsPanel({ logs }) {
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

  return (
    <div className="logs-panel">
      <div className="panel-header">
        <h2>📝 运行日志</h2>
        <p className="log-count">共 {logs.length} 条记录</p>
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
