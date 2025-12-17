# LigaHikru - React Frontend

Professional React frontend for the LigaHikru AI Document Assistant (RAG system).

## Features

- **Ask**: Chat with AI about your documents, with citations
- **Search**: Search document fragments with relevance scores
- **Upload**: Upload PDF, TXT, or MD files for processing

## Tech Stack

- React 18 with functional components and hooks
- Vite for fast development and building
- TailwindCSS for styling
- Lucide React for icons

## Project Structure

```
react-app/
├── src/
│   ├── components/       # React components
│   │   ├── Header.jsx
│   │   ├── TabNavigation.jsx
│   │   ├── ChatView.jsx
│   │   ├── SearchView.jsx
│   │   ├── UploadView.jsx
│   │   └── Spinner.jsx
│   ├── services/         # API integration
│   │   └── api.js
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles + Tailwind
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend/react-app
   npm install
   ```

2. **Configure environment:**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env if your backend runs on a different URL
   # Default: VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   The app will open automatically at `http://localhost:3000`

## Backend Requirements

Make sure the backend is running at `http://localhost:8000` (or update the `VITE_API_BASE_URL` in `.env`).

The frontend expects these API endpoints:
- `POST /api/chat/ask` - Ask questions
- `POST /api/chat/search` - Search documents
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents/list` - List documents
- `DELETE /api/documents/{filename}` - Delete documents

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` folder.

## Demo Tips

1. Start with the **Ask** tab to show AI-powered Q&A
2. Switch to **Search** to demonstrate semantic search
3. Use **Upload** to show document ingestion (if time permits)
4. Highlight citations and relevance scores in responses
