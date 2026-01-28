# 🎓 Education - AI-Powered Internship Opportunity Matcher

An intelligent job matching system that helps students find the perfect internship opportunities using AI-powered scoring and real-time LinkedIn job scraping.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-purple.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)

---

## 🚀 Features

### Core Functionality
- **Smart Job Matching**: AI-powered scoring algorithm that matches students with internships based on track, skills, academic level, and location preference
- **Real LinkedIn Scraping**: Uses SerpAPI to search LinkedIn jobs with `site:linkedin.com/jobs` operator
- **Multi-Query Search**: Makes 10 different searches with 8 results each for maximum coverage
- **AI-Generated Reasons**: OpenAI generates personalized explanations for why each job matches
- **Intern-Only Filter**: Automatically filters for intern/internship/trainee positions, excludes senior roles

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/match` | POST | Match student profile with internship opportunities |
| `/match/{run_id}` | GET | Retrieve a previous match run by ID |
| `/task-simulation` | POST | Generate realistic internship task scenarios |
| `/health` | GET | Health check endpoint |

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic** - Data validation using Python type annotations

### AI & Workflow
- **LangGraph** - Graph-based workflow orchestration
- **LangChain** - LLM application framework
- **OpenAI GPT-4o-mini** - AI-powered reason generation

### Job Search
- **SerpAPI** - Google Search API for LinkedIn job scraping
- **Requests** - HTTP library for API calls

### Data & Storage
- **Python Dataclasses** - Structured data models
- **In-memory Store** - Fast result caching

---

## 📁 Project Structure

```
Education/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   │
│   ├── api/                 # API Endpoints
│   │   ├── __init__.py
│   │   ├── match.py         # /match endpoint
│   │   └── task_simulation.py
│   │
│   ├── graph/               # LangGraph Workflow
│   │   ├── __init__.py
│   │   ├── state.py         # Workflow state definition
│   │   ├── nodes.py         # 7 processing nodes
│   │   └── workflow.py      # Graph compilation
│   │
│   ├── models/              # Data Models
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic schemas
│   │
│   ├── services/            # External Services
│   │   ├── __init__.py
│   │   ├── linkedin_client.py   # LinkedIn via SerpAPI
│   │   ├── openai_client.py     # AI reason generation
│   │   ├── search_client.py     # Search abstraction
│   │   └── task_simulation.py
│   │
│   └── agents/              # AI Agents
│       └── __init__.py
│
├── scripts/
│   └── sample_run.py        # Sample workflow execution
│
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🔄 Workflow Pipeline

The LangGraph workflow processes requests through 7 nodes:

```
┌─────────────────┐
│  User Profile   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 1. Normalize    │  → Categorize skills (hard/tools/soft)     [Rule-based]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Build Query  │  → Generate LinkedIn search queries        [Agent]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Retrieve     │  → 10 searches × 8 results = 80 max jobs   [Rule-based]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. Clean        │  → Deduplicate and normalize data          [Rule-based]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Score        │  → Multi-criteria scoring (0-100)          [Rule-based]
│                 │  → AI generates match reasons               [Agent]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Rank         │  → Sort by score, diversify by company     [Rule-based]
└────────┬────────┘
         ▼
┌─────────────────┐
│ 7. Build Result │  → Final JSON response                     [Rule-based]
└─────────────────┘
```

### Node Types Legend
| Type | Description |
|------|-------------|
| **Rule-based** | Deterministic logic using predefined rules, mappings, and algorithms |
| **🤖 Agent** | AI-powered using OpenAI GPT-4o-mini for intelligent responses |

### Agent Details
- **Score Node (Agent)**: Uses OpenAI to generate personalized, context-aware reasons explaining why each job matches the student's profile. Considers job description, company, skills alignment, and career goals.

---

## 📊 Scoring Algorithm

Jobs are scored on a 100-point scale:

| Criteria | Points | Description |
|----------|--------|-------------|
| Track Alignment | 25 | Match with user's track/major |
| Skills Match | 30 | Overlap with user's skills |
| Academic Fit | 10 | Year level appropriateness |
| Location Preference | 15 | Egypt/Remote/Abroad match |
| Readiness Level | 10 | Intern vs Senior position |
| Platform Quality | 5 | Source reliability (LinkedIn = 5) |
| Company Reputation | 5 | Known tech companies bonus |

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Education
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key
SEARCH_API_KEY=your-serpapi-key
SEARCH_PROVIDER=serpapi
MAX_RESULTS=100
TOP_K=5
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 API Usage

### Match Endpoint

**Request:**
```bash
POST /match
Content-Type: application/json

{
  "academic_year": 3,
  "preference": "egypt",
  "track": "data science",
  "skills": ["python", "sql", "pandas", "machine learning", "data analysis"],
  "notes": "Looking for summer internship"
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "created_at": "2026-01-28T00:00:00",
  "normalized_profile": {
    "year_level": "junior",
    "track": "data science",
    "location_preference": "egypt",
    "skills": {
      "hard": ["data analysis", "machine learning"],
      "tools": ["pandas", "python", "sql"],
      "soft": []
    }
  },
  "opportunities_top20": [...],
  "ranked_top5": [
    {
      "title": "Data Science Intern",
      "company": "talabat",
      "location": "Egypt",
      "url": "https://linkedin.com/jobs/view/...",
      "score": 85,
      "reasons": [
        "Perfect match for your Data Science track",
        "Your Python and SQL skills align with requirements",
        "talabat is a leading tech company in Egypt"
      ]
    }
  ]
}
```

---

## 🔍 Search Strategy

- ✅ Only `/jobs/view/` URLs (individual job pages)
- ✅ Posted in last month (`tbs: qdr:m`)
- ❌ Excludes senior/lead/manager positions
- ❌ Excludes search result pages

---

## 🏢 Supported Tracks

| Track | Search Keywords |
|-------|----------------|
| Data Science | Data Science Intern, Data Analyst Intern, Analytics Intern |
| Machine Learning | ML Engineer Intern, AI Intern, Deep Learning Intern |
| Software Engineering | Software Engineer Intern, SWE Intern, Developer Intern |
| Backend | Backend Intern, API Developer Intern, Node.js Intern |
| Frontend | Frontend Intern, React Intern, UI Developer Intern |
| Full Stack | Full Stack Intern, Web Developer Intern |
| DevOps | DevOps Intern, SRE Intern, Cloud Intern |
| Mobile | iOS Intern, Android Intern, Flutter Intern |
| Cybersecurity | Security Analyst Intern, InfoSec Intern |
| Data Engineering | Data Engineer Intern, ETL Intern, Big Data Intern |

---

## 🎮 Task Simulation Feature

Generate realistic internship task scenarios for interview preparation and skill assessment.

### What It Does
- Creates **realistic workplace scenarios** based on actual Egyptian tech companies
- Simulates real engineering tasks you might encounter as an intern
- Includes company context, business problems, constraints, and deliverables
- Helps students prepare for technical interviews and assess job readiness

### Supported Companies (13 Egyptian Tech Companies)

| Company | Type | Focus Areas |
|---------|------|-------------|
| **Vodafone Egypt** | Telecommunications | Mobile services, IoT, digital payments |
| **Orange Egypt** | Telecommunications | Telecom infrastructure, cloud solutions |
| **Valeo Egypt** | Automotive Tech | Driver assistance systems, sensors |
| **IBM Egypt** | Enterprise Tech | Cloud computing, AI, enterprise software |
| **Microsoft Egypt** | Software & Cloud | Azure, Office 365, enterprise solutions |
| **Swvl** | Transportation Startup | Mass transit, route optimization |
| **Instabug** | Developer Tools SaaS | Mobile monitoring, bug reporting |
| **Fawry** | Fintech | Digital payments, e-commerce |
| **Paymob** | Payment Processing | Online payment gateway, merchant APIs |
| **Noon Academy** | EdTech | Online education, live classes |
| **Vezeeta** | HealthTech | Healthcare booking, telemedicine |
| **Elmenus** | FoodTech | Restaurant discovery, food delivery |
| **Dell Egypt** | Enterprise Hardware | IT infrastructure, support services |

### API Usage

**List Available Companies:**
```bash
GET /companies
```

**Generate Task Simulation:**
```bash
POST /task-simulation
Content-Type: application/json

{
  "company_name": "Instabug",
  "task_title": "Build a Crash Analytics Dashboard"
}
```

**Response Example:**
```
==========================================
TASK SIMULATION: Build a Crash Analytics Dashboard @ Instabug
==========================================

COMPANY PROFILE
- Name: Instabug
- Type: Developer Tools SaaS
- Size: Series B Startup
- Focus Areas: Mobile app monitoring, bug reporting, crash analytics
- Tech Stack: Swift, Kotlin, JavaScript, Node.js, MongoDB, AWS

1. COMPANY CONTEXT
   - Business problem: Real-time data processing challenges...
   - Users: Mobile developers, QA teams, product managers...

2. TASK ORIGIN
   - Trigger: 30% increase in customer support tickets...
   - Constraints: 2-week sprint, existing MongoDB schema...

3. AMBIGUITY AREAS
   - What data granularity is needed?
   - Which crash types should be prioritized?

4. DELIVERABLES
   - Working dashboard prototype
   - API documentation
   - Performance benchmarks

5. EVALUATION RUBRIC
   - Code quality: 30%
   - Problem-solving approach: 25%
   - Communication: 20%
   - Technical decisions: 25%
```

---
