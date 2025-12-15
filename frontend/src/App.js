import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './components/Dashboard';
import GradesList from './components/GradesList';
import LogsPanel from './components/LogsPanel';

function App() {
  const [status, setStatus] = useState({
    is_running: false,
    last_check_time: null,
    next_check_time: null,
    total_courses: 0,
    current_gpa: 0.0,
    today_new_count: 0
  });
  const [grades, setGrades] = useState([]);
  const [dailyGrades, setDailyGrades] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // 每5秒刷新一次
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statusRes, gradesRes, dailyRes, logsRes] = await Promise.all([
        axios.get('/api/status'),
        axios.get('/api/grades'),
        axios.get('/api/daily'),
        axios.get('/api/logs')
      ]);

      setStatus(statusRes.data);
      setGrades(gradesRes.data);
      setDailyGrades(dailyRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error('获取数据失败:', error);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>🎓 成绩监控系统</h1>
        <p>南京林业大学 - Grade Monitor</p>
      </header>

      <nav className="nav-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveTab('dashboard')}
        >
          📊 仪表盘
        </button>
        <button 
          className={activeTab === 'grades' ? 'active' : ''} 
          onClick={() => setActiveTab('grades')}
        >
          📚 成绩列表
        </button>
        <button 
          className={activeTab === 'logs' ? 'active' : ''} 
          onClick={() => setActiveTab('logs')}
        >
          📝 运行日志
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard 
            status={status} 
            dailyGrades={dailyGrades}
            allGrades={grades}
          />
        )}
        {activeTab === 'grades' && (
          <GradesList 
            grades={grades}
            dailyGrades={dailyGrades}
          />
        )}
        {activeTab === 'logs' && (
          <LogsPanel logs={logs} />
        )}
      </main>

      <footer className="footer">
        <p>系统状态: <span className={status.is_running ? 'status-running' : 'status-stopped'}>
          {status.is_running ? '● 运行中' : '○ 已停止'}
        </span></p>
        <p>最后更新: {new Date().toLocaleString('zh-CN')}</p>
      </footer>
    </div>
  );
}

export default App;
