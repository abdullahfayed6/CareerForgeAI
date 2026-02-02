# Practical Project Recommender Agent 🚀

## Overview

The **Practical Project Recommender Agent** is a specialized AI system designed to convert learning topics into hands-on, portfolio-ready projects with professional GitHub repository structuring guidance.

### Mission

🎯 **Prevent students from staying in theory mode**  
🎯 **Push them toward industry-style building**  
🎯 **Create employable portfolios with professional projects**  
🎯 **Teach real-world engineering practices**

---

## Features

### 1️⃣ Project Recommendations

Provides **3-6 practical projects** across difficulty levels:

- ✅ **Beginner Projects**: Entry-level builds for skill foundation
- ✅ **Intermediate Projects**: Real-world applications
- ✅ **Advanced Projects**: Production-ready, enterprise-level systems

Each project includes:
- **What You'll Build**: Detailed deliverable description
- **Skills Gained**: 4-6 specific technical skills
- **Real-Work Connection**: How it mirrors industry tasks
- **CV Value**: Why it's valuable for portfolios
- **Relevant Roles**: 3-5 job titles that benefit
- **Tech Stack**: Technologies and tools used
- **Estimated Duration**: Realistic completion time

### 2️⃣ Professional GitHub Guidance

For **each project**, receive comprehensive GitHub structuring advice:

#### Repository Structure
- Professional repository naming conventions
- Folder structure tailored to tech stack
- Proper `.gitignore`, `.env.example`, config files

#### README Template
Guidance on essential sections:
- Project Overview & Problem Statement
- Key Features & Capabilities
- Tech Stack & Architecture
- Setup Instructions & Usage
- Screenshots/Demo
- Testing & Deployment
- Future Improvements

#### Professional Practices
- ✅ Conventional commit messages
- ✅ Feature branch workflow
- ✅ Comprehensive documentation
- ✅ Sample data & API examples
- ✅ Unit testing strategies
- ✅ CI/CD setup (GitHub Actions)

#### Sample Commit Messages
```
feat: Add user authentication with JWT
fix: Resolve database connection pooling issue
docs: Update API endpoint documentation
refactor: Extract validation logic into middleware
test: Add integration tests for payment flow
```

### 3️⃣ YouTube Project Playlists

Curated **4-8 YouTube playlists** focused on:
- ✅ **Building real projects** (no theory-only content)
- ✅ Step-by-step implementation tutorials
- ✅ Mixed difficulty levels
- ✅ Popular, high-quality channels

Each playlist includes:
- Exact title and channel name
- What project(s) are built
- Difficulty level
- Total duration
- Direct YouTube link

---

## API Endpoints

### POST `/project/recommend`

Generate practical project recommendations.

**Request Body:**
```json
{
  "topic": "Full-Stack Web Development",
  "current_level": "intermediate",
  "time_available": "moderate",
  "focus_on_portfolio": true,
  "max_projects": 6
}
```

**Response:**
```json
{
  "topic": "Full-Stack Web Development",
  "topic_summary": "Building modern web applications...",
  "projects": [
    {
      "name": "E-Commerce REST API",
      "level": "intermediate",
      "description": "Full-featured e-commerce backend",
      "what_you_will_build": "A production-ready RESTful API...",
      "skills_gained": ["REST API design", "Authentication", "Database design"],
      "real_work_connection": "E-commerce backends are essential...",
      "cv_value": "Demonstrates ability to build scalable APIs...",
      "relevant_roles": ["Backend Developer", "Full-Stack Engineer"],
      "tech_stack": ["Node.js", "Express", "MongoDB", "JWT"],
      "estimated_duration": "3-4 weeks",
      "github_guidance": {
        "repo_name": "ecommerce-rest-api",
        "folder_structure": "/src\n  /controllers\n  /models\n...",
        "readme_should_contain": ["Project Overview", "Features", "Setup"],
        "professional_practices": ["Clear commit messages", "Feature branches"],
        "sample_commit_messages": ["feat: Add user auth", "fix: Database timeout"]
      },
      "match_score": 90,
      "icon": "💼"
    }
  ],
  "youtube_project_playlists": [
    {
      "title": "Build a Full-Stack MERN E-Commerce App",
      "focus": "Complete e-commerce platform with cart and payments",
      "level": "intermediate",
      "url": "https://youtube.com/...",
      "channel": "Traversy Media",
      "duration": "12 hours / 25 videos",
      "icon": "🎬"
    }
  ],
  "why_build_projects": [
    "Practical application of theoretical knowledge",
    "Builds a portfolio employers actually review"
  ],
  "portfolio_tips": [
    "Add a 'Live Demo' link in README",
    "Include GIFs showing key features"
  ],
  "next_steps": [
    "Start with the beginner project",
    "Set up GitHub repository properly"
  ]
}
```

### POST `/project/recommend-sync`

Synchronous version of the recommendation endpoint.

### GET `/project/health`

Health check endpoint.

---

## Usage Examples

### Python Client

```python
import asyncio
from app.agents.project_recommender import PracticalProjectRecommenderAgent
from app.models.recommender_schemas import ProjectRequest

async def get_projects():
    agent = PracticalProjectRecommenderAgent()
    
    request = ProjectRequest(
        topic="Machine Learning with Python",
        current_level="beginner",
        time_available="extensive",
        focus_on_portfolio=True,
        max_projects=5
    )
    
    result = await agent.recommend(request)
    
    for project in result.projects:
        print(f"Project: {project.name}")
        print(f"Level: {project.level}")
        print(f"Tech Stack: {', '.join(project.tech_stack)}")
        print(f"GitHub Repo: {project.github_guidance.repo_name}")
        print()

asyncio.run(get_projects())
```

### HTTP Request

```bash
curl -X POST "http://localhost:8000/project/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Cloud Computing with AWS",
    "current_level": "intermediate",
    "time_available": "moderate",
    "focus_on_portfolio": true,
    "max_projects": 4
  }'
```

---

## Integration with Event Recommender

The Event Recommender Agent now also includes project recommendations! When you request events/hackathons, you'll receive:

- Traditional events (hackathons, workshops, competitions)
- **+ Practical project recommendations**
- **+ YouTube project playlists**

This ensures students get both **external opportunities** and **hands-on building guidance**.

---

## Supported Topics

The agent works with any technical topic:

- **Web Development**: React, Vue, Angular, Node.js, Django, etc.
- **Mobile Development**: React Native, Flutter, iOS, Android
- **Data Science/ML**: Python, TensorFlow, PyTorch, scikit-learn
- **Backend/API**: REST APIs, GraphQL, Microservices
- **Cloud & DevOps**: AWS, Azure, Docker, Kubernetes
- **Blockchain**: Smart contracts, DApps, Web3
- **Game Development**: Unity, Unreal Engine
- **And more...**

---

## Project Structure Examples

### Backend API
```
/src
  /controllers
  /models
  /routes
  /middleware
  /services
  /utils
/tests
/config
/docs
README.md
.env.example
.gitignore
package.json
```

### Frontend App
```
/src
  /components
  /pages
  /hooks
  /services
  /utils
  /assets
/public
/tests
README.md
.gitignore
package.json
```

### Full-Stack App
```
/client
  /src
  /public
/server
  /src
  /config
/shared
/docs
README.md
docker-compose.yml
.gitignore
```

### Data Science Project
```
/data
  /raw
  /processed
/notebooks
/src
  /models
  /features
/tests
/models
/reports
README.md
requirements.txt
.gitignore
```

---

## Why Build Projects?

✅ **Practical Application**: Theory → Practice  
✅ **Portfolio Building**: Showcase real skills  
✅ **Interview Material**: Concrete examples to discuss  
✅ **Skill Validation**: Prove you can build  
✅ **Problem-Solving**: Learn by doing  
✅ **Employability**: Stand out from theory-only candidates

---

## Portfolio Tips

1. **Live Demos**: Deploy projects and add live links
2. **Visual Proof**: Include screenshots, GIFs, or videos
3. **Clean README**: Professional documentation
4. **Code Quality**: Follow best practices
5. **Problem-Solving**: Document challenges you solved
6. **Impact**: Explain the value/use case

---

## Testing

Run the sample script:

```bash
python scripts/sample_project_recommender.py
```

This will generate recommendations for:
- Full-Stack Web Development
- Data Science & Machine Learning
- Mobile App Development

---

## Architecture

```
┌─────────────────────────────────────┐
│   User Request (Topic + Level)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  PracticalProjectRecommenderAgent   │
│  - Analyzes topic                   │
│  - Generates projects               │
│  - Provides GitHub guidance         │
│  - Curates YouTube playlists        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PracticalProjectResponse          │
│   - Projects (beginner→advanced)    │
│   - YouTube playlists               │
│   - GitHub structuring tips         │
│   - Portfolio guidance              │
└─────────────────────────────────────┘
```

---

## Files Modified/Created

### New Files
- `app/agents/project_recommender.py` - Main agent implementation
- `app/api/project.py` - API endpoints
- `scripts/sample_project_recommender.py` - Test script
- `docs/PROJECT_RECOMMENDER.md` - This documentation

### Modified Files
- `app/models/recommender_schemas.py` - Added new models
- `app/agents/recommender_prompts.py` - Added project prompt
- `app/agents/event_recommender.py` - Integrated projects
- `app/main.py` - Registered new router

---

## Future Enhancements

- [ ] Integration with GitHub API for repo creation
- [ ] Code templates/boilerplates generation
- [ ] Project complexity estimation
- [ ] Automated project roadmap
- [ ] Integration with learning platforms
- [ ] Project collaboration matching

---

## License

Part of the CareerForgeAI Education Platform
