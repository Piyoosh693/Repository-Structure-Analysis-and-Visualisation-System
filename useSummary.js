import { useState } from 'react';
import apiClient from '../utils/apiClient';

export function useSummary() {
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);
  const [currentFile, setCurrentFile] = useState(null);

  const fetchSummary = async (node, repoRoot) => {
    // Validate inputs
    if (!node || !node.data.path || !repoRoot) {
      setSummaryError('Missing required data: node path or repo root');
      return;
    }

    // Cache hit: same file and summary already loaded
    if (node.data.path === currentFile && summary !== null) {
      return;
    }

    try {
      setSummaryLoading(true);
      setSummaryError(null);
      setCurrentFile(node.data.path);

      // Send complete SummarizeRequest with all required fields
      const response = await apiClient.post('/api/summarize', {
        filepath: node.data.path,           // relative path
        repo_root: repoRoot,                // absolute path to repo
        language: node.data.language,       // language from node
        // content_hash is optional and computed by backend if omitted
      });

      setSummary(response.data.summary);
    } catch (err) {
      const errorMsg = err.message || err.response?.data?.detail || 'Failed to fetch summary';
      setSummaryError(errorMsg);
      setSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  };

  const clearSummary = () => {
    setSummary(null);
    setSummaryError(null);
    setCurrentFile(null);
  };

  return {
    summary,
    summaryLoading,
    summaryError,
    currentFile,
    fetchSummary,
    clearSummary,
  };
}
