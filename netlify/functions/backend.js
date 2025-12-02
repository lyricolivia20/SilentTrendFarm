/**
 * Main Backend API Handler for Netlify Functions
 * Provides all backend functionality in serverless environment
 */

// Node 18+ has native fetch, no import needed

// Helper function for CORS headers
const getCORSHeaders = () => ({
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Content-Type': 'application/json'
});

// Mock database for stats (in production, use a real database)
const getStats = () => ({
  total_posts: 42,
  total_views: 15234,
  categories: {
    'indie-dev': 15,
    'ai-ml': 12,
    'it-tech': 15
  },
  last_updated: new Date().toISOString()
});

// Generate blog ideas based on category
const generateBlogIdeas = (category = 'tech', count = 5) => {
  const templates = {
    'ai-ml': [
      'Building Your First {tool} Model',
      'Understanding {concept} in Machine Learning',
      '{framework} vs {alternative}: A Comparison',
      'How to Implement {algorithm} from Scratch',
      'Real-world Applications of {technology}'
    ],
    'indie-dev': [
      'From Idea to Launch: Building {project}',
      'Marketing Your Indie {product} in 2024',
      'Tools Every Indie Developer Needs for {task}',
      'Monetizing Your {creation}: A Guide',
      'Building a Community Around Your {product}'
    ],
    'it-tech': [
      'Getting Started with {technology}',
      'Best Practices for {process}',
      'Optimizing {system} Performance',
      'Security Considerations for {platform}',
      'The Future of {field}: Trends to Watch'
    ]
  };

  const topics = {
    'ai-ml': ['TensorFlow', 'PyTorch', 'Neural Networks', 'GPT', 'Computer Vision'],
    'indie-dev': ['SaaS', 'Mobile App', 'Game', 'Newsletter', 'Course'],
    'it-tech': ['Kubernetes', 'DevOps', 'Serverless', 'Microservices', 'Edge Computing']
  };

  const ideas = [];
  const categoryTemplates = templates[category] || templates['it-tech'];
  const categoryTopics = topics[category] || topics['it-tech'];

  for (let i = 0; i < Math.min(count, categoryTemplates.length); i++) {
    const template = categoryTemplates[i];
    const topic = categoryTopics[i % categoryTopics.length];
    
    ideas.push({
      title: template.replace(/{[^}]+}/g, topic),
      description: `Explore the latest insights and best practices related to ${topic}`,
      keywords: [topic.toLowerCase(), category],
      category
    });
  }

  return ideas;
};

// Get trending topics (mock data for now, can integrate with real APIs)
const getTrendingTopics = async (keywords = []) => {
  // In production, you could call Google Trends API or other trend services
  const mockTrends = {
    'AI': { interest: 95, related: ['ChatGPT', 'Machine Learning', 'Neural Networks'] },
    'web development': { interest: 88, related: ['React', 'Next.js', 'TypeScript'] },
    'programming': { interest: 82, related: ['Python', 'JavaScript', 'Rust'] }
  };

  const results = {};
  for (const keyword of keywords) {
    results[keyword] = mockTrends[keyword] || { interest: Math.floor(Math.random() * 100), related: [] };
  }

  return {
    keywords,
    trends: results,
    timestamp: new Date().toISOString()
  };
};

// Analyze content from URL
const analyzeContent = async (url) => {
  try {
    const response = await fetch(url);
    const html = await response.text();
    
    // Basic analysis (in production, use proper HTML parsing)
    const titleMatch = html.match(/<title>(.*?)<\/title>/i);
    const descMatch = html.match(/<meta\s+name="description"\s+content="(.*?)"/i);
    const h1Matches = html.match(/<h1[^>]*>(.*?)<\/h1>/gi) || [];
    
    return {
      url,
      meta_data: {
        title: titleMatch ? titleMatch[1] : '',
        description: descMatch ? descMatch[1] : '',
        h1_count: h1Matches.length,
        word_count: html.replace(/<[^>]*>/g, '').split(/\s+/).length
      },
      analyzed_at: new Date().toISOString()
    };
  } catch (error) {
    throw new Error(`Failed to analyze URL: ${error.message}`);
  }
};

// AI Assistant (mock implementation - integrate with OpenAI in production)
const aiAssistant = async (prompt, maxTokens = 150) => {
  // Check for OpenAI API key in environment
  const apiKey = process.env.OPENAI_API_KEY;
  
  if (apiKey) {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            { role: 'system', content: 'You are a helpful blog writing assistant.' },
            { role: 'user', content: prompt }
          ],
          max_tokens: maxTokens
        })
      });
      
      const data = await response.json();
      return {
        response: data.choices[0].message.content,
        tokens_used: data.usage.total_tokens
      };
    } catch (error) {
      console.error('OpenAI API error:', error);
    }
  }
  
  // Fallback mock response
  return {
    response: `This is a mock response for: "${prompt}". Configure OPENAI_API_KEY for real AI responses.`,
    tokens_used: 0
  };
};

// Main handler
exports.handler = async (event, context) => {
  const headers = getCORSHeaders();
  const path = event.path.replace('/.netlify/functions/backend', '');
  const method = event.httpMethod;

  // Handle preflight requests
  if (method === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    // Parse body if present
    const body = event.body ? JSON.parse(event.body) : {};

    // Route handling
    switch (path) {
      case '':
      case '/':
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            message: 'SilentTrendFarm API is running on Netlify Functions',
            version: '1.0.0',
            endpoints: [
              '/health',
              '/stats',
              '/trends',
              '/generate-ideas',
              '/analyze-content',
              '/ai-assistant'
            ]
          })
        };

      case '/health':
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            platform: 'netlify-functions'
          })
        };

      case '/stats':
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(getStats())
        };

      case '/trends':
        if (method !== 'POST') {
          return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
        }
        const trends = await getTrendingTopics(body.keywords || ['AI', 'web development']);
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(trends)
        };

      case '/generate-ideas':
        if (method !== 'POST') {
          return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
        }
        const ideas = generateBlogIdeas(body.category, body.count);
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            ideas,
            generated_at: new Date().toISOString()
          })
        };

      case '/analyze-content':
        if (method !== 'POST') {
          return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
        }
        if (!body.url) {
          return { statusCode: 400, headers, body: JSON.stringify({ error: 'URL is required' }) };
        }
        const analysis = await analyzeContent(body.url);
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(analysis)
        };

      case '/ai-assistant':
        if (method !== 'POST') {
          return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
        }
        if (!body.prompt) {
          return { statusCode: 400, headers, body: JSON.stringify({ error: 'Prompt is required' }) };
        }
        const aiResponse = await aiAssistant(body.prompt, body.max_tokens);
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(aiResponse)
        };

      default:
        return {
          statusCode: 404,
          headers,
          body: JSON.stringify({
            error: 'Endpoint not found',
            path: path
          })
        };
    }
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message
      })
    };
  }
};
