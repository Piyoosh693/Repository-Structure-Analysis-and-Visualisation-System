import { useState } from 'react';

export default function Toolbar({ onAnalyze, loading }) {
  const [repoPath, setRepoPath] = useState('');
  const [inputFocused, setInputFocused] = useState(false);

  const toolbarStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '56px',
    background: 'var(--bg-secondary)',
    borderBottom: '1px solid var(--border-color)',
    display: 'flex',
    alignItems: 'center',
    padding: '0 20px',
    gap: '12px',
    zIndex: 100,
  };

  const titleContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    marginRight: '16px',
    whiteSpace: 'nowrap',
  };

  const logoStyle = {
    color: 'var(--accent-purple)',
    fontSize: '20px',
    fontWeight: '700',
  };

  const titleStyle = {
    color: 'var(--text-primary)',
    fontSize: '16px',
    fontWeight: '700',
  };

  const inputStyle = {
    flex: 1,
    maxWidth: '500px',
    background: 'var(--bg-tertiary)',
    border: `1px solid ${inputFocused ? 'var(--accent-blue)' : 'var(--border-color)'}`,
    borderRadius: '6px',
    padding: '8px 14px',
    color: 'var(--text-primary)',
    fontSize: '13px',
    fontFamily: 'inherit',
    outline: 'none',
    transition: 'border-color 0.2s',
  };

  const isDisabled = loading || repoPath.trim() === '';

  const buttonStyle = {
    background: isDisabled ? 'var(--bg-tertiary)' : 'var(--accent-blue)',
    color: isDisabled ? 'var(--text-secondary)' : '#0d1117',
    padding: '8px 18px',
    borderRadius: '6px',
    border: 'none',
    fontWeight: '600',
    fontSize: '13px',
    cursor: isDisabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap',
  };

  const handleClick = () => {
    if (!isDisabled) {
      onAnalyze(repoPath);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !isDisabled) {
      onAnalyze(repoPath);
    }
  };

  return (
    <div style={toolbarStyle}>
      <div style={titleContainerStyle}>
        <span style={logoStyle}>{'{}' }</span>
        <span style={titleStyle}>CodeLens</span>
      </div>
      <input
        type="text"
        placeholder="Enter absolute path to repository... e.g. /home/user/my-project"
        value={repoPath}
        onChange={(e) => setRepoPath(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setInputFocused(true)}
        onBlur={() => setInputFocused(false)}
        style={inputStyle}
      />
      <button
        onClick={handleClick}
        disabled={isDisabled}
        style={buttonStyle}
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
  );
}
