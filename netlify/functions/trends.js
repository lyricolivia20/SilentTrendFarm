/**
 * Netlify Function - Trends API
 * Fetches trending topics and generates content ideas
 */

// Node 18+ has native fetch, no import needed

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    if (event.httpMethod === 'GET') {
      // Mock trending data for demonstration
      // In production, you'd integrate with actual trend APIs
      const trendingTopics = [
        { topic: 'AI Development', score: 95, category: 'ai-ml' },
        { topic: 'Web3 Technologies', score: 88, category: 'it-tech' },
        { topic: 'Indie Game Development', score: 82, category: 'indie-dev' },
        { topic: 'Cloud Computing', score: 79, category: 'it-tech' },
        { topic: 'Machine Learning', score: 76, category: 'ai-ml' }
      ];

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          trends: trendingTopics,
          timestamp: new Date().toISOString()
        })
      };
    }

    if (event.httpMethod === 'POST') {
      const body = JSON.parse(event.body || '{}');
      const { category = 'tech', count = 5 } = body;

      // Generate blog ideas based on category
      const ideas = generateBlogIdeas(category, count);

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          ideas,
          category,
          generated_at: new Date().toISOString()
        })
      };
    }

    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};

function generateBlogIdeas(category, count) {
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
}
