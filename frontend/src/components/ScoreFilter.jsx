import React from 'react';
import './ScoreFilter.css';

const ScoreFilter = ({ minScore, maxScore, currentScore, onScoreChange }) => {
  return (
    <div className="score-filter">
      <div className="score-filter-content">
        <label htmlFor="score-slider">Minimum Score: {currentScore}</label>
        <input
          type="range"
          id="score-slider"
          min={minScore}
          max={maxScore}
          value={currentScore}
          onChange={(e) => onScoreChange(Number(e.target.value))}
          step="0.1"
        />
      </div>
    </div>
  );
};

export default ScoreFilter; 