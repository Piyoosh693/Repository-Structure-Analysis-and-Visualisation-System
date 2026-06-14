import MetricsBadge from './MetricsBadge';
import { getLanguageColor } from '../utils/colorScale';

export default function SidePanel({
  selectedNode,
  summary,
  summaryLoading,
  summaryError,
  onClose,
}) {
  const panelStyle = {
    position: 'fixed',
    top: '56px',
    right: 0,
    bottom: 0,
    width: '320px',
    background: 'var(--bg-secondary)',
    borderLeft: '1px solid var(--border-color)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    zIndex: 50,
    transform: selectedNode ? 'translateX(0)' : 'translateX(100%)',
    transition: 'transform 0.25s ease',
    pointerEvents: selectedNode ? 'auto' : 'none',
  };

  const headerStyle = {
    padding: '16px',
    borderBottom: '1px solid var(--border-color)',
    flexShrink: 0,
  };

  const headerTopStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '8px',
  };

  const languageDotStyle = {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    flexShrink: 0,
  };

  const fileNameStyle = {
    fontSize: '14px',
    fontWeight: '700',
    color: 'var(--text-primary)',
    margin: 0,
  };

  const closeButtonStyle = {
    background: 'none',
    border: 'none',
    color: 'var(--text-secondary)',
    fontSize: '18px',
    cursor: 'pointer',
    padding: 0,
    lineHeight: 1,
    transition: 'color 0.2s',
  };

  const pathStyle = {
    fontSize: '11px',
    color: 'var(--text-secondary)',
    marginTop: '6px',
    wordBreak: 'break-all',
  };

  const metricsStyle = {
    padding: '12px 16px',
    borderBottom: '1px solid var(--border-color)',
    flexShrink: 0,
  };

  const labelStyle = {
    fontSize: '10px',
    fontWeight: '700',
    color: 'var(--text-secondary)',
    letterSpacing: '1px',
    display: 'block',
    marginBottom: '8px',
  };

  const summaryContainerStyle = {
    padding: '16px',
    flex: 1,
    overflowY: 'auto',
  };

  const summaryTextStyle = {
    fontSize: '13px',
    lineHeight: '1.7',
    color: 'var(--text-primary)',
    padding: '10px 12px',
    background: 'var(--bg-tertiary)',
    borderRadius: '6px',
    border: '1px solid var(--border-color)',
  };

  const summaryErrorStyle = {
    color: 'var(--accent-red)',
    fontSize: '12px',
    padding: '10px',
    background: 'rgba(248, 81, 73, 0.1)',
    borderRadius: '6px',
    border: '1px solid rgba(248, 81, 73, 0.3)',
  };

  const emptyStateStyle = {
    color: 'var(--text-secondary)',
    fontSize: '12px',
    fontStyle: 'italic',
  };

  const footerStyle = {
    padding: '12px 16px',
    borderTop: '1px solid var(--border-color)',
    flexShrink: 0,
    fontSize: '10px',
    color: 'var(--text-secondary)',
    textAlign: 'center',
  };

  const skeletonBarStyle = (width) => ({
    width: width,
    height: width === '100%' ? '12px' : '10px',
    background: 'var(--bg-tertiary)',
    borderRadius: '4px',
    marginBottom: '8px',
    animation: 'shimmer 1.2s ease-in-out infinite',
  });

  return (
    <div style={panelStyle}>
      {selectedNode && (
        <>
          {/* HEADER */}
          <div style={headerStyle}>
            <div style={headerTopStyle}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                <div
                  style={{
                    ...languageDotStyle,
                    background: getLanguageColor(selectedNode.data.language),
                  }}
                />
                <h3 style={fileNameStyle}>{selectedNode.data.label}</h3>
              </div>
              <button
                onClick={onClose}
                style={closeButtonStyle}
                onMouseEnter={(e) => (e.target.style.color = 'var(--text-primary)')}
                onMouseLeave={(e) => (e.target.style.color = 'var(--text-secondary)')}
              >
                ×
              </button>
            </div>
            <div style={pathStyle}>{selectedNode.data.path}</div>
          </div>

          {/* METRICS */}
          <div style={metricsStyle}>
            <span style={labelStyle}>METRICS</span>
            <MetricsBadge
              loc={selectedNode.data.loc}
              complexity={selectedNode.data.complexity}
            />
          </div>

          {/* AI SUMMARY */}
          <div style={summaryContainerStyle}>
            <span style={labelStyle}>AI SUMMARY</span>
            {summaryLoading && (
              <div>
                <div style={skeletonBarStyle('100%')} />
                <div style={skeletonBarStyle('85%')} />
                <div style={skeletonBarStyle('70%')} />
              </div>
            )}
            {summaryError && (
              <div style={summaryErrorStyle}>{summaryError}</div>
            )}
            {summary && (
              <div style={summaryTextStyle}>{summary}</div>
            )}
            {!summaryLoading && !summaryError && !summary && (
              <div style={emptyStateStyle}>Click a node to generate an AI summary</div>
            )}
          </div>

          {/* FOOTER */}
          <div style={footerStyle}>
            Powered by AI · Summaries cached per file hash
          </div>
        </>
      )}
    </div>
  );
}
