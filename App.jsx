import { useState } from 'react';
import GraphCanvas from './components/GraphCanvas';
import SidePanel from './components/SidePanel';
import Toolbar from './components/Toolbar';
import { useGraphData } from './hooks/useGraphData';
import { useSummary } from './hooks/useSummary';

export default function App() {
  const [selectedNode, setSelectedNode] = useState(null);
  const { graphData, loading, error, fetchGraph, repoRoot } = useGraphData();
  const { summary, summaryLoading, summaryError, fetchSummary, clearSummary } = useSummary();

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    // Pass both node object and repoRoot to fetchSummary
    if (repoRoot) {
      fetchSummary(node, repoRoot);
    }
  };

  const handleClosePanel = () => {
    setSelectedNode(null);
    clearSummary();
  };

  const handleAnalyze = (repoPath) => {
    if (repoPath.trim() === '') {
      return;
    }
    setSelectedNode(null);
    clearSummary();
    fetchGraph(repoPath);
  };

  return (
    <div
      style={{
        height: '100vh',
        width: '100vw',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-primary)',
        overflow: 'hidden',
      }}
    >
      <Toolbar onAnalyze={handleAnalyze} loading={loading} />

      {/* Error banner */}
      {error && (
        <div
          style={{
            position: 'fixed',
            top: 56,
            left: 0,
            right: 0,
            background: 'rgba(248, 81, 73, 0.15)',
            borderBottom: '1px solid rgba(248, 81, 73, 0.4)',
            color: '#f85149',
            padding: '10px 20px',
            fontSize: 13,
            zIndex: 99,
          }}
        >
          ⚠ {error}
        </div>
      )}

      {/* Main canvas area, padded for toolbar */}
      <div
        style={{
          position: 'fixed',
          top: 56,
          left: 0,
          right: selectedNode ? '320px' : '0px',
          bottom: 0,
          transition: 'right 0.25s ease',
        }}
      >
        <GraphCanvas graphData={graphData} onNodeClick={handleNodeClick} loading={loading} />
      </div>

      <SidePanel
        selectedNode={selectedNode}
        summary={summary}
        summaryLoading={summaryLoading}
        summaryError={summaryError}
        onClose={handleClosePanel}
      />
    </div>
  );
}
