# SilentTrendFarm

An automated affiliate marketing website that generates SEO-optimized content based on trending topics. The site automatically updates weekly with viral products and trending topics, integrating affiliate links and ad revenue opportunities.

## 🚀 Features

- **Automated Content Generation**: Fetches trending topics from Google Trends API
- **AI-Powered Articles**: Uses OpenAI GPT-4 to generate 800-1200 word SEO-optimized articles
- **Affiliate Integration**: Automatically embeds Amazon and ClickBank affiliate links
- **Ad Revenue**: Google AdSense integration with optimized ad placements
- **Static Site**: Built with Astro for fast loading and SEO
- **Weekly Updates**: GitHub Actions automation for weekly content updates

## 📁 Project Structure

```
/
├── public/
├── src/
│   ├── layouts/
│   │   └── Layout.astro          # Main site layout with analytics
│   ├── pages/
│   │   ├── index.astro           # Homepage listing all posts
│   │   └── posts/[...slug].astro # Individual post pages
│   ├── content/
│   │   ├── config.ts             # Content collection schema
│   │   └── posts/                # Markdown blog posts
│   └── styles/
│       └── global.css            # Tailwind CSS
├── scripts/
│   ├── trend_fetcher.py          # Google Trends API integration
│   ├── content_generator.py      # OpenAI content generation
│   └── generate_post.py          # Main automation script
├── .github/workflows/
│   └── update-site.yml           # Weekly automation workflow
├── netlify.toml                  # Netlify deployment config
├── requirements.txt             # Python dependencies
└── package.json                  # Node.js dependencies
```

## 🛠️ Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- OpenAI API key
- Google Analytics ID
- Google AdSense Publisher ID

### Installation

1. Clone the repository
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
5. Update the following in your environment:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_ANALYTICS_ID`: Your GA measurement ID
   - `ADSENSE_PUB_ID`: Your AdSense publisher ID

6. Update affiliate links in the generated content templates

## 🧞 Commands

| Command | Action |
| :--- | :--- |
| `npm run dev` | Starts local dev server at `localhost:4321` |
| `npm run build` | Build your production site to `./dist/` |
| `npm run preview` | Preview your build locally, before deploying |
| `python scripts/generate_post.py` | Manually generate a new trending post |

## 🤖 Automation

The site automatically updates weekly via GitHub Actions:

- **Schedule**: Every Sunday at midnight UTC
- **Process**: 
  1. Fetches trending topic from Google Trends
  2. Generates SEO article using OpenAI
  3. Embeds affiliate links
  4. Builds and deploys the site

You can also trigger updates manually via the GitHub Actions UI.

## 🚀 Deployment

### Netlify (Recommended)

1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variables in Netlify dashboard
5. Deploy!

### Manual Deployment

```bash
npm run build
# Deploy the dist/ folder to your hosting provider
```

## 💰 Monetization

### Affiliate Marketing
- **Amazon Associates**: Update affiliate tag in generated links
- **ClickBank**: Configure your ClickBank links in the content generator
- **Other Networks**: Modify the affiliate link generation logic

### Ad Revenue
- **Google AdSense**: Update publisher ID in Layout.astro
- **Google Analytics**: Track traffic and user behavior
- **Additional Networks**: Can be added via custom components

## 🔧 Customization

### Content Generation
Edit `scripts/content_generator.py` to:
- Change article length and style
- Modify SEO optimization
- Update affiliate link patterns
- Add new monetization networks

### Site Design
- Modify `src/layouts/Layout.astro` for site structure
- Update Tailwind classes in components
- Add custom CSS in `src/styles/global.css`

### Automation Schedule
Edit `.github/workflows/update-site.yml` to change update frequency.

## 📈 SEO Optimization

- **Meta Tags**: Automatically generated for each post
- **Structured Data**: Built into Astro's content collections
- **URL Structure**: SEO-friendly slugs from titles
- **Image Optimization**: Use Astro's image optimization
- **Performance**: Static site for fast loading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
