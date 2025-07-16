export async function getKnowledgeGraph() {
  console.log('Fetching knowledge graph from backend...');
  try {
    const response = await fetch('http://localhost:8089/knowledge-graph');
    console.log('Response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to fetch knowledge graph: ${response.status}`);
    }
    const data = await response.json();
    console.log('Knowledge graph API response:', data);
    return data;
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}
