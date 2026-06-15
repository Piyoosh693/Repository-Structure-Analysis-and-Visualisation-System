import { useState, memo } from 'react';
import { Handle, Position } from 'reactflow';
import { getComplexityColor, getLoCColor, getLanguageColor } from '../utils/colorScale';

function FileNode({ data, selected }) {
  const [isHovered, setIsHovered] = useState(false);

  const containerStyle = {
    width: '180px',
    background: 'var(--bg-secondary)',
    border: `1px solid ${isHovered || selected ? 'var(--accent-blue)' : 'var(--border-color)'}`,
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: selected ? '0 0 0 2px rgba(88, 166, 255, 0.3)' : 'none',
    overflow: 'hidden',
  };

  const languageBarStyle = {
    height: '3px',
    background: getLanguageColor(data.language),
    width: '100%',
  };

  const contentStyle = {
    padding: '10px 12px',
  };

  const topRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px',
  };

  const labelStyle = {
    fontWeight: '600',
    fontSize: '12px',
    color: 'var(--text-primary)',
    maxWidth: '120px',
  };

  const badgeStyle = {
    fontSize: '10px',
    color: 'var(--text-secondary)',
    background: 'var(--bg-tertiary)',
    padding: '1px 6px',
    borderRadius: '10px',
  };

  const metricsRowStyle = {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  };

  const metricStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  };

  const dotStyle = (color) => ({
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: color,
  });

  const metricTextStyle = {
    fontSize: '11px',
    color: 'var(--text-secondary)',
  };

  const handleStyle = {
    background: '#58a6ff',
    width: '8px',
    height: '8px',
    border: '2px solid var(--bg-secondary)',
  };

  return (
    <div
      style={containerStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={languageBarStyle} />
      <div style={contentStyle}>
        <div style={topRowStyle}>
          <span style={labelStyle} className="truncate">
            {data.label}
          </span>
          <span style={badgeStyle}>{data.language || '?'}</span>
        </div>
        <div style={metricsRowStyle}>
          <div style={metricStyle}>
            <div style={dotStyle(getLoCColor(data.loc))} />
            <span style={metricTextStyle}>{(data.loc ?? '?')} LoC</span>
          </div>
          {data.complexity !== null && data.complexity !== undefined && (
            <div style={metricStyle}>
              <div style={dotStyle(getComplexityColor(data.complexity))} />
              <span style={metricTextStyle}>CC {data.complexity}</span>
            </div>
          )}
        </div>
      </div>
      <Handle
        type="target"
        position={Position.Top}
        style={handleStyle}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={handleStyle}
      />
    </div>
  );
}

export default memo(FileNode);
