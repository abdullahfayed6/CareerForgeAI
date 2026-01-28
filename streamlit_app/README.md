# Education Platform - Streamlit Web App

A modern web interface for the Education Platform Multi-Agent System.

## Features

- **📝 Interview System** - Practice adaptive technical and behavioral interviews
- **🎯 Career Translator** - Convert lectures into industry-relevant skills
- **🔍 Opportunity Matcher** - Find matching internship opportunities
- **🏢 Task Simulation** - Experience real-world company tasks

## Setup

### 1. Install Dependencies

```bash
cd streamlit_app
pip install -r requirements.txt
```

### 2. Start the FastAPI Backend

Make sure the FastAPI server is running on `http://localhost:8000`:

```bash
cd ..
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run the Streamlit App

```bash
cd streamlit_app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
streamlit_app/
├── app.py                    # Main entry point
├── pages/
│   ├── 1_Interview.py        # Interview system page
│   ├── 2_Career.py           # Career translator page
│   ├── 3_Match.py            # Opportunity matcher page
│   └── 4_Task_Simulation.py  # Task simulation page
├── utils/
│   ├── __init__.py
│   ├── api_client.py         # Centralized API client
│   └── styles.py             # Custom CSS styles
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Configuration

### Environment Variables

- `API_BASE_URL` - Backend API URL (default: `http://localhost:8000`)

### Streamlit Config

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server port
- Other Streamlit settings

## Usage

### Interview System

1. Configure interview settings (role, experience, tech stack)
2. Click "Start Interview"
3. Answer questions in the chat interface
4. View real-time evaluations and feedback
5. Get final report when complete

### Career Translator

1. Enter lecture topic
2. Optionally add lecture notes
3. Select target career track
4. Click "Translate to Career Value"
5. Explore industry use cases, tasks, and career impact

### Opportunity Matcher

1. Fill in your academic profile
2. Select your skills
3. Set location preference
4. Click "Find Matching Opportunities"
5. View ranked opportunities with match reasons

### Task Simulation

1. Select or enter a company name
2. Select or enter a task title
3. Click "Generate Task Simulation"
4. Review the realistic task scenario
5. Use it for practice or portfolio building
