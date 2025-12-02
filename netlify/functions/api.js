/**
 * Netlify Function - Main API Handler
 * This serverless function handles API requests for the backend
 */

exports.handler = async (event, context) => {
  const path = event.path.replace(/\/api\/.*/, '');
  const method = event.httpMethod;
  
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle preflight requests
  if (method === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Route handlers
    if (event.path === '/api/health') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          function: 'netlify-serverless'
        })
      };
    }

    if (event.path === '/api/stats') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          total_posts: 42,
          total_views: 15234,
          categories: {
            'indie-dev': 15,
            'ai-ml': 12,
            'it-tech': 15
          },
          last_updated: new Date().toISOString()
        })
      };
    }

    // Default response
    return {
      statusCode: 404,
      headers,
      body: JSON.stringify({
        error: 'Endpoint not found',
        path: event.path
      })
    };
  } catch (error) {
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
