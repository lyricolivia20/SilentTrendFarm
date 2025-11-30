# LyriCodes Field Notes

A collection of guides and insights for aspiring developers, digital artists, and creators navigating the complex and exhilarating world of independent development. Built with Astro, Tailwind CSS v4, and Starwind UI.

## 🚀 Features

- **Three Content Sections**: Indie Dev's Playbook, ML Diaries, Troubleshoot.exe
- **Neon Cyberpunk Aesthetic**: Cyan/purple/pink color scheme with glass morphism
- **Category-Based Navigation**: Color-coded sections (emerald, cyan, violet)
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Static Site**: Built with Astro for fast loading and SEO
- **Markdown Content**: Easy-to-edit blog posts with frontmatter

## 📁 Project Structure

```
/
├── public/
├── src/
│   ├── layouts/
│   │   └── Layout.astro          # Main site layout with navigation
│   ├── pages/
│   │   ├── index.astro           # Homepage with category sections
│   │   ├── about.astro           # About page with projects & tech stack
│   │   ├── stack.astro           # Detailed technology stack breakdown
│   │   └── posts/[...slug].astro # Individual post pages
│   ├── content/
│   │   ├── config.ts             # Content collection schema
│   │   └── posts/                # Markdown blog posts (13 articles)
│   └── styles/
│       └── global.css            # Tailwind CSS with prose styling
└── package.json                  # Node.js dependencies
```

## 🛠️ Setup

### Prerequisites
- Node.js 18+

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 🧞 Commands

| Command | Action |
| :--- | :--- |
| `npm run dev` | Starts local dev server at `localhost:4321` |
| `npm run build` | Build your production site to `./dist/` |
| `npm run preview` | Preview your build locally, before deploying |

## 📚 Content Categories

### The Indie Dev's Playbook (Emerald)
Game development, worldbuilding, engine choices, and technical troubleshooting.
- Worldbuilding a Cyberpunk Universe
- Choosing Your Engine (Unity, Unreal, Godot)
- Unity Crash Course
- Building 3D Worlds on the Web (A-Frame, Three.js)
- SQL for Game Devs

### ML Diaries (Cyan)
Practical AI & ML projects, from training models to prompt engineering.
- Stable Diffusion LoRA Training
- Prompt Engineering Mastery
- Designing AI-Powered Apps (WhereTF Case Study)
- Debugging Python AI Scripts

### Troubleshoot.exe (Violet)
IT & tech troubleshooting guides for common problems.
- Wi-Fi Channel Analysis with Wireshark
- Home Network Troubleshooting
- MBR vs. GPT Partitions
- PC Build Hardware Troubleshooting

## 🎨 Adding New Posts

Create a new `.md` file in `src/content/posts/` with frontmatter:

```markdown
---
title: "Your Post Title"
description: "A brief description of the post"
pubDate: 2024-11-30
heroImage: /images/your-image.jpg
tags:
  - "tag1"
  - "tag2"
category: "indie-dev"  # or "ai-ml" or "it-tech"
---

Your content here...
```

## 🚀 Deployment

### Netlify (Recommended)

1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Deploy!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
