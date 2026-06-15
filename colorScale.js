export function getComplexityColor(complexity) {
  if (complexity === null || complexity === undefined) {
    return '#58a6ff';
  }
  if (complexity < 5) {
    return '#3fb950';
  }
  if (complexity < 10) {
    return '#d29922';
  }
  if (complexity < 20) {
    return '#f0883e';
  }
  return '#f85149';
}

export function getLoCColor(loc) {
  if (loc === null || loc === undefined) {
    return '#8b949e';
  }
  if (loc < 50) {
    return '#3fb950';
  }
  if (loc < 200) {
    return '#d29922';
  }
  if (loc < 500) {
    return '#f0883e';
  }
  return '#f85149';
}

export function getLanguageColor(language) {
  const colorMap = {
    'Python': '#3572A5',
    'JavaScript': '#f1e05a',
    'TypeScript': '#3178c6',
    'Java': '#b07219',
    'C': '#555555',
    'C++': '#f34b7d',
    'Go': '#00ADD8',
    'Rust': '#dea584',
    'Ruby': '#701516',
    'PHP': '#4F5D95',
  };
  return colorMap[language] || '#8b949e';
}
