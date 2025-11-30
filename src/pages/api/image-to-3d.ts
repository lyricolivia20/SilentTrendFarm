import type { APIRoute } from 'astro';

export const POST: APIRoute = async ({ request }) => {
  try {
    const { imageUrl } = await request.json();
    
    if (!imageUrl) {
      return new Response(JSON.stringify({ error: 'No image URL provided' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const MESHY_API_KEY = import.meta.env.MESHY_API_KEY || 'msy_SjCfcDpzXXstAi41mz3V3RTq9yXplQzQxoWe';

    // Step 1: Create the image-to-3D task
    const createResponse = await fetch('https://api.meshy.ai/v1/image-to-3d', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${MESHY_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: imageUrl,
        enable_pbr: true,
      }),
    });

    if (!createResponse.ok) {
      const error = await createResponse.text();
      console.error('Meshy create error:', error);
      return new Response(JSON.stringify({ error: 'Failed to start 3D generation' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const createData = await createResponse.json();
    const taskId = createData.result;

    if (!taskId) {
      return new Response(JSON.stringify({ error: 'No task ID returned' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Step 2: Poll for completion (max 5 minutes)
    let attempts = 0;
    const maxAttempts = 60; // 60 * 5 seconds = 5 minutes

    while (attempts < maxAttempts) {
      await new Promise(r => setTimeout(r, 5000)); // Wait 5 seconds

      const statusResponse = await fetch(`https://api.meshy.ai/v1/image-to-3d/${taskId}`, {
        headers: { 'Authorization': `Bearer ${MESHY_API_KEY}` },
      });

      if (!statusResponse.ok) {
        attempts++;
        continue;
      }

      const statusData = await statusResponse.json();

      if (statusData.status === 'SUCCEEDED') {
        return new Response(JSON.stringify({ 
          success: true,
          modelUrl: statusData.model_urls?.glb || statusData.model_urls?.obj
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      } else if (statusData.status === 'FAILED') {
        return new Response(JSON.stringify({ error: '3D generation failed' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Still processing, continue polling
      attempts++;
    }

    return new Response(JSON.stringify({ error: 'Timeout waiting for 3D model' }), {
      status: 504,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('API error:', error);
    return new Response(JSON.stringify({ error: 'Server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
