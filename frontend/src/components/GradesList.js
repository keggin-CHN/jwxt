import React, { useState } from 'react';
import './GradesList.css';

function GradesList({ grades, dailyGrades }) {
  const [sortBy, setSortBy] = useState('default');
  const [filterText, setFilterText] = useState('');

  const isNewToday = (grade) => {
    return dailyGrades.some(dg => dg.课程编号 === grade.课程编号);
  };

  let filteredGrades = grades.filter(grade => 
    grade.课程名称.toLowerCase().includes(filterText.toLowerCase()) ||
    grade.课程编号.toLowerCase().includes(filterText.toLowerCase())
  );

  if (sortBy === 'score-desc') {
    filteredGrades.sort((a, b) => parseFloat(b.成绩 || 0) - parseFloat(a.成绩 || 0));
  } else if (sortBy === 'score-asc') {
    filteredGrades.sort((a, b) => parseFloat(a.成绩 || 0) - parseFloat(b.成绩 || 0));
  } else if (sortBy === 'gpa-desc') {
    filteredGrades.sort((a, b) => parseFloat(b.绩点 || 0) - parseFloat(a.绩点 || 0));
  } else if (sortBy === 'gpa-asc') {
    filteredGrades.sort((a, b) => parseFloat(a.绩点 || 0) - parseFloat(b.绩点 || 0));
  } else if (sortBy === 'credit-desc') {
    filteredGrades.sort((a, b) => parseFloat(b.学分 || 0) - parseFloat(a.学分 || 0));
  }

  return (
    <div className="grades-list">
      <div className="list-header">
        <h2>📚 全部成绩 ({filteredGrades.length})</h2>
        <div className="controls">
          <input
            type="text"
            placeholder="搜索课程名称或编号..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="search-input"
          />
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="default">默认排序</option>
            <option value="score-desc">成绩从高到低</option>
            <option value="score-asc">成绩从低到高</option>
            <option value="gpa-desc">绩点从高到低</option>
            <option value="gpa-asc">绩点从低到高</option>
            <option value="credit-desc">学分从高到低</option>
          </select>
        </div>
      </div>

      <div className="grades-table-container">
        <table className="grades-table">
          <thead>
            <tr>
              <th>课程编号</th>
              <th>课程名称</th>
              <th>成绩</th>
              <th>学分</th>
              <th>绩点</th>
              <th>开课学期</th>
              <th>课程性质</th>
            </tr>
          </thead>
          <tbody>
            {filteredGrades.map((grade, index) => (
              <tr 
                key={index} 
                className={isNewToday(grade) ? 'new-today' : ''}
              >
                <td>{grade.课程编号}</td>
                <td>
                  {grade.课程名称}
                  {isNewToday(grade) && <span className="new-badge">NEW</span>}
                </td>
                <td className="score">{grade.成绩}</td>
                <td>{grade.学分}</td>
                <td className="gpa">{grade.绩点}</td>
                <td>{grade.开课学期}</td>
                <td>{grade.课程性质}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredGrades.length === 0 && (
          <div className="no-data">
            <p>暂无成绩数据</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default GradesList;
