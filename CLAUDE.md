# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static web application that provides 25+ utility tools including random number generators, text processing, data conversion tools, and developer utilities. The project is built as a pure frontend solution with no backend dependencies.

## Development Commands

```bash
# Start local development server
npm run dev
# or
npm start
# Both run: python -m http.server 8000

# Access at http://localhost:8000

# Build (no-op for static site)
npm run build
```

## Architecture

This is a multi-page static website with the following structure:

- **index.html** - Main navigation hub with category-based tool organization
- **random.html** - Random number generation tools
- **generators.html** - Custom generators (colors, passwords, names, decisions)
- **games.html** - Interactive games (spin wheel, lottery, dice, guessing games)
- **data-tools.html** - Data processing tools (UUID, QR codes, Base64, JSON, timestamps)
- **text-tools.html** - Text processing utilities (statistics, case conversion, deduplication)
- **dev-tools.html** - Developer tools (regex tester, color picker, CSS gradient generator)

### Key Technical Details

- **Language**: Chinese (zh-CN) interface
- **Styling**: Each page contains embedded CSS with consistent gradient backgrounds and glassmorphism design
- **JavaScript**: Vanilla JS embedded in each HTML file (no external dependencies except QR code generation)
- **Privacy-focused**: All processing happens client-side
- **Responsive**: Mobile-friendly design

### Common CSS Pattern
All pages use similar styling with:
- Gradient background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Glassmorphism containers with `backdrop-filter: blur(10px)`
- Consistent color scheme and typography

### Deployment
- Configured for Vercel with security headers in vercel.json
- Also deployable to GitHub Pages
- Static site - no build process required