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

export async function analyzeLastUploadedTxt() {
  // Get the list of documents (assume sorted by upload_date desc)
  const docsRes = await fetch('http://localhost:8089/documents?limit=1&skip=0');
  if (!docsRes.ok) throw new Error('Failed to fetch documents');
  const docsData = await docsRes.json();
  const lastDoc = docsData.documents && docsData.documents.length > 0 ? docsData.documents[0] : null;
  if (!lastDoc || !lastDoc.filename.endsWith('.txt')) {
    throw new Error('No .txt file found in uploads');
  }
  // Trigger analysis
  const analyzeRes = await fetch('http://localhost:8089/document-analysis/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      document_id: lastDoc.id,
      analysis_types: ['knowledge_extraction']
    })
  });
  if (!analyzeRes.ok) throw new Error('Failed to trigger document analysis');
  return await analyzeRes.json();
}

export async function analyzeDocumentById(documentId: string) {
  // Trigger analysis for a specific document
  const analyzeRes = await fetch('http://localhost:8089/document-analysis/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      document_id: documentId,
      analysis_types: ['knowledge_extraction']
    })
  });
  if (!analyzeRes.ok) throw new Error('Failed to trigger document analysis');
  return await analyzeRes.json();
}

// Training API functions
export async function getTrainingCategories() {
  console.log('Fetching training categories from backend...');
  try {
    const response = await fetch('http://localhost:8089/training/categories');
    console.log('Training categories response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to fetch training categories: ${response.status}`);
    }
    const data = await response.json();
    console.log('Training categories API response:', data);
    return data;
  } catch (error) {
    console.error('Training categories API error:', error);
    throw error;
  }
}

export async function getTrainingQuestions(category: string, limit?: number) {
  console.log(`Fetching training questions for category: ${category}`);
  try {
    let url = `http://localhost:8089/training/questions/${encodeURIComponent(category)}?all_questions=true`;
    
    if (limit) {
      url += `&limit=${limit}`;
    }
    
    const response = await fetch(url);
    console.log('Training questions response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to fetch training questions: ${response.status}`);
    }
    const data = await response.json();
    console.log('Training questions API response:', data);
    return data;
  } catch (error) {
    console.error('Training questions API error:', error);
    throw error;
  }
}

export async function saveTrainingAnswer(answerData: any) {
  console.log('Saving training answer:', answerData);
  try {
    const response = await fetch('http://localhost:8089/training/answer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answerData),
    });
    console.log('Save answer response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to save training answer: ${response.status}`);
    }
    const data = await response.json();
    console.log('Save answer API response:', data);
    return data;
  } catch (error) {
    console.error('Save answer API error:', error);
    throw error;
  }
}

export async function getTrainingData(category?: string, limit?: number) {
  console.log(`Fetching training data for category: ${category || 'all'}`);
  try {
    let url = 'http://localhost:8089/training/data';
    const params = new URLSearchParams();
    
    if (category) params.append('category', category);
    if (limit) params.append('limit', limit.toString());
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    const response = await fetch(url);
    console.log('Training data response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to fetch training data: ${response.status}`);
    }
    const data = await response.json();
    console.log('Training data API response:', data);
    return data;
  } catch (error) {
    console.error('Training data API error:', error);
    throw error;
  }
}

export async function getTrainingSession(sessionId: string) {
  console.log(`Fetching training session: ${sessionId}`);
  try {
    const response = await fetch(`http://localhost:8089/training/session/${sessionId}`);
    console.log('Training session response status:', response.status);
    if (!response.ok) {
      throw new Error(`Failed to fetch training session: ${response.status}`);
    }
    const data = await response.json();
    console.log('Training session API response:', data);
    return data;
  } catch (error) {
    console.error('Training session API error:', error);
    throw error;
  }
}
