import { getComplexityColor, getLoCColor } from '../utils/colorScale';

export default function MetricsBadge({ loc, complexity }) {
  const containerStyle = {
    display: 'flex',
    gap: '6px',
    flexWrap: 'wrap',
  };

  const pillStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    padding: '3px 8px',
    borderRadius: '12px',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border-color)',
  };

  const dotStyle = (color) => ({
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: color,
  });

  const textStyle = {
    fontSize: '11px',
    color: 'var(--text-secondary)',
  };

  return (
    <div style={containerStyle}>
      <div style={pillStyle}>
        <div style={dotStyle(getLoCColor(loc))} />
        <span style={textStyle}>{loc} lines</span>
      </div>
      {complexity !== null && complexity !== undefined && (
        <div style={pillStyle}>
          <div style={dotStyle(getComplexityColor(complexity))} />
          <span style={textStyle}>Complexity: {complexity}</span>
        </div>
      )}
    </div>
  );
}
