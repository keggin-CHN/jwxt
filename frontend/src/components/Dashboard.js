import React from 'react';
import './Dashboard.css';

function Dashboard({ status, dailyGrades, allGrades }) {
  const calculateAverage = (grades) => {
    if (grades.length === 0) return 0;
    const scores = grades.filter(g => !isNaN(parseFloat(g.成绩))).map(g => parseFloat(g.成绩));
    if (scores.length === 0) return 0;
    return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2);
  };

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h3>总课程数</h3>
            <p className="stat-value">{status.total_courses}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>当前GPA</h3>
            <p className="stat-value">{status.current_gpa.toFixed(2)}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>总学分</h3>
            <p className="stat-value">{status.total_credits ? status.total_credits.toFixed(1) : '0.0'}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>今日新增</h3>
            <p className="stat-value">{status.today_new_count}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>平均分</h3>
            <p className="stat-value">{calculateAverage(allGrades)}</p>
          </div>
        </div>
      </div>

      <div className="monitor-status">
        <h2>📡 监控状态</h2>
        <div className="status-info">
          <div className="status-item">
            <span className="label">运行状态:</span>
            <span className={status.is_running ? 'value running' : 'value stopped'}>
              {status.is_running ? '● 运行中' : '○ 已停止'}
            </span>
          </div>
          <div className="status-item">
            <span className="label">最后检查:</span>
            <span className="value">{status.last_check_time || '暂无'}</span>
          </div>
          <div className="status-item">
            <span className="label">下次检查:</span>
            <span className="value">{status.next_check_time || '暂无'}</span>
          </div>
        </div>
      </div>

      {dailyGrades.length > 0 && (
        <div className="today-grades">
          <h2>🎉 今日新增成绩</h2>
          <div className="today-list">
            {dailyGrades.map((grade, index) => (
              <div key={index} className="today-item">
                <span className="course-name">{grade.课程名称}</span>
                <span className="course-score">{grade.成绩}</span>
                <span className="course-gpa">绩点: {grade.绩点}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
