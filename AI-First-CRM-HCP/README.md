# AI-First CRM - Healthcare Professional (HCP) Module

An AI-powered CRM system for pharmaceutical field representatives to log and manage HCP interactions. Built with **React + Redux** frontend, **FastAPI** backend, **LangGraph** agent framework, and **Groq LLM** (gemma2-9b-it).

---

## Architecture Overview

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   Frontend (React + Redux)  │────▶│   Backend (FastAPI)         │
│   Port: 5173                │     │   Port: 8000                │
│                             │     │                             │
│  ┌───────────────────────┐  │     │  ┌───────────────────────┐  │
│  │ Left: AI-Populated    │  │     │  │ API Routes            │  │
│  │       Form            │  │     │  │ /api/interactions     │  │
│  └───────────────────────┘  │     │  └──────────┬────────────┘  │
│                             │     │             │               │
│  ┌───────────────────────┐  │     │  ┌──────────▼────────────┐  │
│  │ Right: Chat Interface │  │     │  │ LangGraph Agent       │  │
│  │ (gemma2-9b-it)        │  │     │  │ ┌──────────────────┐  │  │
│  └───────────────────────┘  │     │  │ │ Planner Node     │  │  │
└─────────────────────────────┘     │  │ ├──────────────────┤  │  │
                                    │  │ │ Router           │  │  │
                                    │  │ ├──────────────────┤  │  │
                                    │  │ │ 5 Tool Nodes:    │  │  │
                                    │  │ │ 1. Log           │  │  │
                                    │  │ │ 2. Edit          │  │  │
                                    │  │ │ 3. Follow-up     │  │  │
                                    │  │ │ 4. Insights      │  │  │
                                    │  │ │ 5. Materials     │  │  │
                                    │  │ └──────────────────┘  │  │
                                    │  └───────────────────────┘  │
                                    │             │               │
                                    │  ┌──────────▼────────────┐  │
                                    │  │ SQLite / PostgreSQL    │  │
                                    │  └───────────────────────┘  │
                                    └─────────────────────────────┘
```

---

## Features

### Two-Panel Interface
- **Left Panel**: AI-populated interaction form — fields are auto-filled by the LangGraph agent. No manual entry required. Fields populated by AI are marked with a green border and "AI" badge.
- **Right Panel**: Conversational chat interface — describe interactions naturally, and the agent processes them through LangGraph.

### 5 LangGraph AI Agent Tools

| Tool | Intent | Description |
|------|--------|-------------|
| **Log Interaction** | `log` | Extracts structured data from natural language using the LLM (entity extraction, summarization) and saves to database |
| **Edit Interaction** | `edit` | Intelligently identifies only the specific field(s) to update from a correction message (e.g., "Actually it was Dr John") |
| **Follow-up Suggestion** | `followup` | Analyzes interaction sentiment and products discussed to recommend date, priority, and next action |
| **HCP Insights** | `insights` | Queries past interactions for an HCP and generates trend analysis, preferred topics, and strategic recommendations |
| **Material Recommendation** | `materials` | Recommends relevant marketing/sales materials (clinical brochures, dosing cards, etc.) with talking points |

### Tech Stack
- **Frontend**: React 18, Redux Toolkit, Vite, Axios
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **AI Agent**: LangGraph (StateGraph), LangChain
- **LLM**: Groq API - `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (fallback)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Font**: Google Inter (300-800 weights)

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+
- A Groq API key from https://console.groq.com

### 1. Clone and Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and set your Groq API key:
# GROQ_API_KEY=gsk_your_actual_key_here
# MODEL_NAME=gemma2-9b-it
# DATABASE_URL=sqlite:///./crm.db

# Initialize database
python -c "from app.config.init_db import create_tables; create_tables()"

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: **http://localhost:8000**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### 3. Verify Everything Works

1. Open http://localhost:5173 in your browser
2. Type a natural language interaction in the chat panel:
   > "I met Dr. Sarah Chen today at Mercy Hospital. She's a cardiologist. We discussed our new hypertension drug CardioVasc. She was very positive and asked for samples."

3. The AI agent will:
   - Detect intent as `log`
   - Extract all fields (name, specialty, hospital, products, sentiment)
   - Populate the left form panel automatically
   - Return a success confirmation

4. Try editing: "Actually, the hospital was City General."
   - The agent detects `edit` intent
   - Updates only the hospital field

5. Try requesting follow-up suggestions, insights, or materials.

---

## Project Structure

```
AI-First-CRM-HCP/
├── README.md
├── backend/
│   ├── .env                          # Environment variables
│   ├── requirements.txt              # Python dependencies
│   └── app/
│       ├── main.py                   # FastAPI app entry point
│       ├── agent/
│       │   ├── graph.py              # LangGraph StateGraph builder
│       │   ├── state.py              # AgentState TypedDict
│       │   ├── planner.py            # Intent detection (LLM-based)
│       │   ├── router.py             # Conditional routing
│       │   └── nodes.py              # Node function definitions
│       ├── tools/
│       │   ├── log_interaction.py    # Tool 1: Log interaction
│       │   ├── edit_interaction.py   # Tool 2: Edit interaction
│       │   ├── followup_tool.py      # Tool 3: Follow-up suggestions
│       │   ├── hcp_insights.py       # Tool 4: HCP insights
│       │   └── material_recommendation.py  # Tool 5: Material recommendations
│       ├── llm/
│       │   ├── groq_client.py        # Groq LLM client initialization
│       │   └── parser.py             # JSON extraction from LLM responses
│       ├── prompts/
│       │   └── interaction_prompt.py # System prompts for extraction
│       ├── models/
│       │   └── interaction.py        # SQLAlchemy Interaction model
│       ├── schemas/
│       │   └── interaction.py        # Pydantic schemas
│       ├── config/
│       │   ├── settings.py           # App settings
│       │   ├── database.py           # Database engine & session
│       │   └── init_db.py            # Table creation
│       └── api/
│           └── routes/
│               └── interaction.py    # REST API endpoints
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx                  # React entry point
│       ├── App.jsx                   # Root component
│       ├── styles/
│       │   └── global.css            # Global styles (Inter font, CSS vars)
│       ├── redux/
│       │   ├── store.js              # Redux store configuration
│       │   └── slices/
│       │       ├── interactionSlice.js  # Form state management
│       │       └── chatSlice.js         # Chat state & async thunks
│       ├── pages/
│       │   └── LogInteraction/
│       │       └── LogInteraction.jsx   # Two-panel main page
│       └── components/
│           ├── Layout/
│           │   └── Header.jsx
│           ├── Form/
│           │   └── InteractionForm.jsx  # AI-populated form
│           └── Chat/
│               └── ChatPanel.jsx        # Chat interface
└── docker/
    ├── docker-compose.yml
    ├── backend.Dockerfile
    └── frontend.Dockerfile
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/interactions/chat` | **Main endpoint** — sends user message through LangGraph agent |
| GET | `/api/interactions/` | List all interactions |
| POST | `/api/interactions/` | Create interaction manually |
| GET | `/api/interactions/{id}` | Get interaction by ID |
| PUT | `/api/interactions/{id}` | Update interaction |
| DELETE | `/api/interactions/{id}` | Delete interaction |
| GET | `/api/interactions/{id}/history` | Get raw conversation history |

### Chat Endpoint Payload

```json
POST /api/interactions/chat
{
  "message": "I met Dr. Sarah Chen at Mercy Hospital...",
  "interaction_id": null,
  "extracted_data": {}
}
```

### Chat Endpoint Response

```json
{
  "success": true,
  "intent": "log",
  "tool_result": {
    "message": "Interaction logged successfully.",
    "interaction_id": 1,
    "interaction": {
      "hcp_name": "Dr. Sarah Chen",
      "specialty": "Cardiology",
      "hospital": "Mercy Hospital",
      "sentiment": "Positive",
      "summary": "Met with cardiologist Dr. Sarah Chen...",
      ...
    }
  },
  "response": "Interaction logged successfully.",
  "interaction_id": 1,
  "extracted_data": { ... }
}
```

---

## LangGraph Agent Flow

1. **User sends message** → Frontend posts to `/api/interactions/chat`
2. **Planner Node** → LLM classifies intent (log/edit/followup/insights/materials)
3. **Router** → Directs to the appropriate tool node
4. **Tool Node** → Executes the specific tool (extracts data, queries DB, calls LLM)
5. **Response Node** → Formats and returns the result
6. **Frontend updates** → Form gets populated with extracted data, chat shows tool output

```
User Input → Planner (Intent Detection) → Router
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
            Log Interaction          Edit Interaction           Follow-up Tool
                    │                         │                         │
                    ▼                         ▼                         ▼
            HCP Insights           Material Recommend              (Response)
                    │                         │
                    └─────────────────────────┘
                                    │
                                    ▼
                              Response Node
                                    │
                                    ▼
                               Client (React)
```

---

## Testing the 5 Tools

Send these messages through the chat interface:

1. **Log Interaction**: `"I met Dr. Sarah Chen today at Mercy Hospital. She's a cardiologist. We discussed CardioVasc hypertension drug. She was very positive and asked for samples."`
2. **Edit Interaction**: `"Actually, the hospital was City General Hospital, not Mercy."`
3. **Follow-up**: `"Suggest a follow-up for my last interaction"`
4. **HCP Insights**: `"Show me insights for Dr. Sarah Chen"`
5. **Material Recommendation**: `"What materials should I bring next time for this cardiologist?"`

---

## Design Decisions

- **Two-panel layout**: Left form auto-populated by AI, right chat for natural language input. The form is a "trust but verify" surface — reps can review AI-extracted data.
- **LangGraph over simple chains**: StateGraph enables conditional routing, tool selection, and a planner-router-tool architecture that's extensible.
- **gemma2-9b-it**: Chosen for fast inference on Groq. llama-3.3-70b-versatile is configured for heavier context.
- **SQLite for dev**: Zero-setup. Switch to PostgreSQL via DATABASE_URL in `.env`.
- **Redux**: Predictable state management for complex two-panel coordination (chat → agent → form updates).

---

## Troubleshooting

- **`GROQ_API_KEY` not set**: The `.env` file must contain a valid Groq API key. Get one at https://console.groq.com
- **Port 5173 in use**: Change the Vite port in `frontend/vite.config.js`
- **Port 8000 in use**: Change the uvicorn port with `--port 8001`
- **Database issues**: Delete `crm.db` and re-run `create_tables()`
- **CORS errors**: The backend allows `localhost:5173` and `127.0.0.1:5173`

---

## License

MIT
