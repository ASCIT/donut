# GPT-SAM Frontend

React-based chat interface using [assistant-ui](https://www.assistant-ui.com/).

## Prerequisites

- Node.js 18+
- npm or yarn

## Development

```bash
cd donut/modules/gpt_sam/frontend

# Install dependencies
npm install

# Start dev server (for testing)
npm run dev
```

## Building for Production

```bash
cd donut/modules/gpt_sam/frontend

# Install dependencies (if not already done)
npm install

# Build to ../static/
npm run build
```

This will output the built files to `donut/modules/gpt_sam/static/`:
- `gpt-sam.js` - Main JavaScript bundle
- `gpt-sam.css` - Styles

## After Building

The Flask app will automatically serve the built files. No additional configuration needed.

## Updating

After making changes to the React code:

1. Run `npm run build`
2. Refresh the Flask app page
