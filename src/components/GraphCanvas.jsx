import { useEffect, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import FileNode from './FileNode';
import { getLanguageColor } from '../utils/colorScale';

const nodeTypes = { fileNode: FileNode };

function GraphCanvasInner({ graphData, onNodeClick, loading }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { fitView } = useReactFlow();

  useEffect(() => {
    if (graphData) {
      setNodes(graphData.nodes || []);
      setEdges(graphData.edges || []);
      setTimeout(() => fitView({ padding: 0.2 }), 50);
    }
  }, [graphData, setNodes, setEdges, fitView]);

  if (!graphData) {
    return (
      <div
        style={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          color: 'var(--text-secondary)',
        }}
      >
        <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.3 }}>
          ⬡
        </div>
        <div style={{ fontSize: '14px' }}>
          Enter a repository path above and click Analyze
        </div>
        <div
          style={{ fontSize: '12px', marginTop: '6px', opacity: 0.6 }}
        >
          Your codebase graph will appear here
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={(event, node) => onNodeClick(node)}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{ type: 'smoothstep', animated: false }}
        style={{ width: '100%', height: '100%' }}
      >
        <Background variant="dots" gap={20} size={1} color="var(--border-color)" />
        <Controls style={{ bottom: 30, left: 20 }} />
        <MiniMap
          nodeColor={(node) => getLanguageColor(node.data.language)}
          style={{ bottom: 30, right: 20, width: 160, height: 100 }}
          maskColor="rgba(13, 17, 23, 0.8)"
        />
      </ReactFlow>
      {loading && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(13, 17, 23, 0.7)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(2px)',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '3px solid rgba(88, 166, 255, 0.3)',
              borderTop: '3px solid #58a6ff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              marginBottom: '16px',
            }}
          />
          <div
            style={{
              color: 'var(--text-primary)',
              fontSize: '14px',
            }}
          >
            Analyzing repository...
          </div>
        </div>
      )}
    </div>
  );
}

export default function GraphCanvas(props) {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
