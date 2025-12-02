# 🚀 Netlify Deployment Guide for SilentTrendFarm

## Backend API Deployment Status

Your backend is now configured for Netlify deployment with serverless functions!

## ✅ What's Been Set Up

### 1. **Serverless Functions**
- **Location**: `/netlify/functions/`
- **Main Function**: `backend.js` - Handles all API endpoints
- **Additional Functions**: `api.js`, `trends.js` - Specialized endpoints

### 2. **API Endpoints Available**
Once deployed, your API will be available at:
- `https://your-site.netlify.app/api/` - API root
- `https://your-site.netlify.app/api/health` - Health check
- `https://your-site.netlify.app/api/stats` - Blog statistics
- `https://your-site.netlify.app/api/trends` - Trending topics
- `https://your-site.netlify.app/api/generate-ideas` - Blog idea generator
- `https://your-site.netlify.app/api/analyze-content` - SEO analyzer
- `https://your-site.netlify.app/api/ai-assistant` - AI content helper

### 3. **Configuration Files**
- **`netlify.toml`**: Configured with redirects from `/api/*` to functions
- **Build settings**: Automatically builds Astro site and deploys functions

## 📋 Deployment Steps

### Option 1: CLI Deployment (Current)
```bash
# Build the site
npm run build

# Deploy to production
netlify deploy --prod
```

### Option 2: Git-based Continuous Deployment
1. Push your code to GitHub/GitLab/Bitbucket
2. Connect repository in Netlify dashboard
3. Auto-deploys on every push to main branch

### Option 3: Manual Upload
1. Run `npm run build`
2. Drag the `dist` folder to Netlify dashboard
3. Functions will be automatically detected

## 🔧 Environment Variables

Add these in Netlify Dashboard → Site Settings → Environment Variables:

```env
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional for enhanced features
SERPAPI_KEY=your_serpapi_key_here
NEWS_API_KEY=your_newsapi_key_here

# Affiliate tracking
AMAZON_AFFILIATE_TAG=youraffiliate-20
CLICKBANK_ID=yourclickbank
```

## 🧪 Testing Your Deployed API

Once deployed, test your API endpoints:

```bash
# Test health endpoint
curl https://your-site.netlify.app/api/health

# Test stats endpoint
curl https://your-site.netlify.app/api/stats

# Test blog idea generation
curl -X POST https://your-site.netlify.app/api/generate-ideas \
  -H "Content-Type: application/json" \
  -d '{"category": "ai-ml", "count": 3}'

# Test trends
curl -X POST https://your-site.netlify.app/api/trends \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["AI", "web development"]}'
```

## 📊 Monitoring

### Netlify Dashboard Features
- **Functions Tab**: View function logs and metrics
- **Analytics**: Track API usage
- **Deploy Logs**: Debug deployment issues

### Function Logs
Access logs at: `https://app.netlify.com/sites/YOUR-SITE/functions`

## 🔄 Updating the Backend

To update your backend functions:

1. **Modify the function files** in `/netlify/functions/`
2. **Test locally**: `netlify dev`
3. **Deploy**: `netlify deploy --prod` or push to Git

## 🎯 Frontend Integration

Your Astro frontend is already configured to use the API:

```javascript
// In your Astro components
import api from '../lib/api.js';

// The API client automatically uses the correct URL
const stats = await api.getStats();
const trends = await api.getTrends(['keyword']);
```

## 🚨 Troubleshooting

### Common Issues

1. **Function timeout (10s default)**
   - Optimize long-running operations
   - Consider background functions for heavy tasks

2. **CORS errors**
   - Already configured in `backend.js`
   - Check browser console for specific errors

3. **Environment variables not working**
   - Set them in Netlify dashboard, not just .env file
   - Redeploy after adding variables

4. **Function not found**
   - Check function name matches redirect in `netlify.toml`
   - Ensure function exports `handler`

## 📈 Next Steps

1. **Add a database**: Consider Netlify's partner integrations:
   - FaunaDB
   - Supabase
   - PlanetScale

2. **Add authentication**: Use Netlify Identity or Auth0

3. **Enhance monitoring**: Add error tracking with Sentry

4. **Scale up**: Upgrade to Netlify Pro for:
   - Longer function timeouts (26s)
   - More concurrent executions
   - Priority support

## 🔗 Useful Links

- [Netlify Functions Docs](https://docs.netlify.com/functions/overview/)
- [Your Site Dashboard](https://app.netlify.com/sites/YOUR-SITE/overview)
- [Function Logs](https://app.netlify.com/sites/YOUR-SITE/functions)
- [Environment Variables](https://app.netlify.com/sites/YOUR-SITE/settings/env)

## ✅ Deployment Checklist

- [ ] Build successful: `npm run build`
- [ ] Functions created in `/netlify/functions/`
- [ ] `netlify.toml` configured with redirects
- [ ] Environment variables set in Netlify dashboard
- [ ] API endpoints tested locally
- [ ] Deployed to Netlify
- [ ] Production API endpoints verified

---

Your backend is ready for production! The serverless architecture ensures scalability and cost-effectiveness.
