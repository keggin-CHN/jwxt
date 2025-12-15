import React, { useState } from 'react';
import './GPACalculator.css';

function GPACalculator({ currentGrades, currentGPA, currentCredits }) {
  const loadSavedCourses = () => {
    try {
      const saved = localStorage.getItem('virtualCourses');
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  };

  const [virtualCourses, setVirtualCourses] = useState(loadSavedCourses());
  const [courseName, setCourseName] = useState('');
  const [courseCredit, setCourseCredit] = useState('');
  const [courseScore, setCourseScore] = useState('');

  const calculateGPAFromScore = (score) => {
    const numScore = parseFloat(score);
    
    if (numScore >= 95) return 4.5;
    if (numScore >= 90) return 4.0;
    if (numScore >= 85) return 3.5;
    if (numScore >= 80) return 3.0;
    if (numScore >= 75) return 2.5;
    if (numScore >= 70) return 2.0;
    if (numScore >= 65) return 1.5;
    if (numScore >= 60) return 1.0;
    return 0.0;
  };

  const addVirtualCourse = () => {
    if (!courseName.trim() || !courseCredit || !courseScore) {
      alert('请填写完整的课程信息');
      return;
    }

    const credit = parseFloat(courseCredit);
    const score = parseFloat(courseScore);

    if (isNaN(credit) || credit <= 0) {
      alert('请输入有效的学分（大于0的数字）');
      return;
    }

    if (isNaN(score) || score < 0 || score > 100) {
      alert('请输入有效的成绩（0-100之间的数字）');
      return;
    }

    const gpa = calculateGPAFromScore(score);

    const newCourse = {
      id: Date.now(),
      name: courseName.trim(),
      credit: credit,
      score: score,
      gpa: parseFloat(gpa)
    };

    const updatedCourses = [...virtualCourses, newCourse];
    setVirtualCourses(updatedCourses);
    localStorage.setItem('virtualCourses', JSON.stringify(updatedCourses));
    
    setCourseName('');
    setCourseCredit('');
    setCourseScore('');
  };

  const removeVirtualCourse = (id) => {
    const updatedCourses = virtualCourses.filter(course => course.id !== id);
    setVirtualCourses(updatedCourses);
    localStorage.setItem('virtualCourses', JSON.stringify(updatedCourses));
  };

  const calculateEstimatedStats = () => {
    const currentWeightedSum = currentGPA * currentCredits;
    
    let virtualCreditsSum = 0;
    let virtualWeightedSum = 0;

    virtualCourses.forEach(course => {
      virtualCreditsSum += course.credit;
      virtualWeightedSum += course.credit * course.gpa;
    });

    const estimatedCredits = currentCredits + virtualCreditsSum;
    const estimatedGPA = estimatedCredits > 0 
      ? (currentWeightedSum + virtualWeightedSum) / estimatedCredits 
      : 0;

    return {
      estimatedCredits: estimatedCredits.toFixed(1),
      estimatedGPA: estimatedGPA.toFixed(2),
      virtualCreditsSum: virtualCreditsSum.toFixed(1),
      gpaChange: (estimatedGPA - currentGPA).toFixed(2)
    };
  };

  const stats = calculateEstimatedStats();

  return (
    <div className="gpa-calculator">
      <div className="calculator-header">
        <h2>🎯 绩点估算器</h2>
        <p className="description">添加未出成绩的课程，预测您的最终GPA</p>
      </div>

      <div className="current-stats">
        <div className="stat-box">
          <span className="stat-label">当前GPA</span>
          <span className="stat-value">{currentGPA.toFixed(2)}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">当前学分</span>
          <span className="stat-value">{currentCredits.toFixed(1)}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">已有课程</span>
          <span className="stat-value">{currentGrades.length}</span>
        </div>
      </div>

      <div className="add-course-form">
        <h3>➕ 添加虚拟课程</h3>
        <div className="form-grid">
          <input
            type="text"
            placeholder="课程名称"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            className="form-input"
          />
          <input
            type="number"
            placeholder="学分"
            value={courseCredit}
            onChange={(e) => setCourseCredit(e.target.value)}
            step="0.5"
            min="0"
            className="form-input"
          />
          <input
            type="number"
            placeholder="成绩 (0-100)"
            value={courseScore}
            onChange={(e) => setCourseScore(e.target.value)}
            min="0"
            max="100"
            className="form-input"
          />
          <button onClick={addVirtualCourse} className="add-btn">
            添加课程
          </button>
        </div>
      </div>

      {virtualCourses.length > 0 && (
        <>
          <div className="virtual-courses-list">
            <h3>📝 虚拟课程列表</h3>
            <div className="courses-table">
              <table>
                <thead>
                  <tr>
                    <th>课程名称</th>
                    <th>学分</th>
                    <th>成绩</th>
                    <th>绩点</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {virtualCourses.map(course => (
                    <tr key={course.id}>
                      <td>{course.name}</td>
                      <td>{course.credit}</td>
                      <td className="score">{course.score}</td>
                      <td className="gpa">{course.gpa}</td>
                      <td>
                        <button 
                          onClick={() => removeVirtualCourse(course.id)}
                          className="remove-btn"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="estimation-result">
            <h3>📊 估算结果</h3>
            <div className="result-grid">
              <div className="result-card">
                <div className="result-icon">📚</div>
                <div className="result-content">
                  <div className="result-label">虚拟课程学分</div>
                  <div className="result-value">{stats.virtualCreditsSum}</div>
                </div>
              </div>
              <div className="result-card">
                <div className="result-icon">🎓</div>
                <div className="result-content">
                  <div className="result-label">估算总学分</div>
                  <div className="result-value">{stats.estimatedCredits}</div>
                </div>
              </div>
              <div className="result-card highlight">
                <div className="result-icon">🌟</div>
                <div className="result-content">
                  <div className="result-label">估算GPA</div>
                  <div className="result-value large">{stats.estimatedGPA}</div>
                </div>
              </div>
              <div className={`result-card ${parseFloat(stats.gpaChange) >= 0 ? 'positive' : 'negative'}`}>
                <div className="result-icon">{parseFloat(stats.gpaChange) >= 0 ? '📈' : '📉'}</div>
                <div className="result-content">
                  <div className="result-label">GPA变化</div>
                  <div className="result-value">
                    {parseFloat(stats.gpaChange) >= 0 ? '+' : ''}{stats.gpaChange}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {virtualCourses.length === 0 && (
        <div className="empty-state">
          <p>💡 还没有添加虚拟课程</p>
          <p className="hint">在上方表单中输入课程信息，点击"添加课程"开始估算</p>
        </div>
      )}
    </div>
  );
}

export default GPACalculator;
