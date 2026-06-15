import { useState } from 'react';
import apiClient from '../utils/apiClient';
import { getLayoutedElements } from '../utils/layoutEngine';

export function useGraphData() {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [repoRoot, setRepoRoot] = useState(null);

  const fetchGraph = async (repoPath) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post('/api/graph', { path: repoPath });

      const { nodes, edges } = response.data;
      
      // Store repo root for later use in summarization
      setRepoRoot(repoPath);

      // Transform nodes to ReactFlow format
      const rfNodes = nodes.map((node) => ({
        id: node.id,
        type: 'fileNode',
        data: {
          label: node.label,
          path: node.path,
          language: node.language,
          loc: node.loc,
          complexity: node.complexity,
          total_lines: node.total_lines,
          blank_lines: node.blank_lines,
          comment_lines: node.comment_lines,
          size_kb: node.size_kb,
        },
        position: { x: 0, y: 0 },
      }));

      // Transform edges to ReactFlow format
      const rfEdges = edges.map((edge, index) => ({
        id: `${edge.source}->${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#58a6ff', strokeWidth: 1.5, opacity: 0.6 },
      }));

      // Auto-layout with dagre
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        rfNodes,
        rfEdges,
        'TB'
      );

      setGraphData({ nodes: layoutedNodes, edges: layoutedEdges });
    } catch (err) {
      const errorMsg = err.message || err.response?.data?.detail || 'Failed to fetch graph';
      setError(errorMsg);
      setGraphData(null);
    } finally {
      setLoading(false);
    }
  };

  return { graphData, loading, error, fetchGraph, repoRoot };
}
