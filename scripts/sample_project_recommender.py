"""Sample script to demonstrate the Practical Project Recommender Agent."""
import asyncio
import json
import logging
from pathlib import Path

from app.agents.project_recommender import PracticalProjectRecommenderAgent
from app.models.recommender_schemas import ProjectRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_project_recommendations():
    """Test practical project recommendations."""
    
    # Initialize agent
    agent = PracticalProjectRecommenderAgent()
    
    # Test case 1: Full-Stack Web Development
    print("\n" + "="*80)
    print("TEST 1: Full-Stack Web Development Projects")
    print("="*80)
    
    request1 = ProjectRequest(
        topic="Full-Stack Web Development with React and Node.js",
        current_level="intermediate",
        time_available="moderate",
        focus_on_portfolio=True,
        max_projects=5
    )
    
    result1 = await agent.recommend(request1)
    
    print(f"\n📊 Topic: {result1.topic}")
    print(f"📝 Summary: {result1.topic_summary}")
    print(f"\n💼 Projects Recommended: {len(result1.projects)}")
    
    for i, project in enumerate(result1.projects, 1):
        print(f"\n{i}. {project.icon} {project.name} [{project.level.upper()}]")
        print(f"   ⏱️  Duration: {project.estimated_duration}")
        print(f"   🎯 Match Score: {project.match_score}%")
        print(f"   📦 Tech Stack: {', '.join(project.tech_stack[:3])}...")
        print(f"   💡 Skills Gained: {', '.join(project.skills_gained[:3])}...")
        print(f"   🏢 Relevant Roles: {', '.join(project.relevant_roles[:2])}...")
        print(f"\n   📂 GitHub Repo: {project.github_guidance.repo_name}")
        print(f"   📋 README Sections: {len(project.github_guidance.readme_should_contain)}")
        print(f"   ✅ Best Practices: {len(project.github_guidance.professional_practices)}")
    
    print(f"\n🎬 YouTube Playlists: {len(result1.youtube_project_playlists)}")
    for i, playlist in enumerate(result1.youtube_project_playlists, 1):
        print(f"\n{i}. {playlist.icon} {playlist.title}")
        print(f"   🎯 Focus: {playlist.focus}")
        print(f"   📊 Level: {playlist.level}")
        print(f"   📺 Channel: {playlist.channel}")
        print(f"   ⏱️  Duration: {playlist.duration}")
    
    print(f"\n💡 Why Build Projects:")
    for reason in result1.why_build_projects[:3]:
        print(f"   • {reason}")
    
    # Test case 2: Data Science & Machine Learning
    print("\n" + "="*80)
    print("TEST 2: Data Science & Machine Learning Projects")
    print("="*80)
    
    request2 = ProjectRequest(
        topic="Machine Learning and Data Science with Python",
        current_level="beginner",
        time_available="extensive",
        focus_on_portfolio=True,
        max_projects=4
    )
    
    result2 = await agent.recommend(request2)
    
    print(f"\n📊 Topic: {result2.topic}")
    print(f"💼 Projects Recommended: {len(result2.projects)}")
    
    for i, project in enumerate(result2.projects, 1):
        print(f"\n{i}. {project.name} [{project.level}]")
        print(f"   What you'll build: {project.what_you_will_build[:100]}...")
        print(f"   Real-world connection: {project.real_work_connection[:100]}...")
    
    # Save detailed output
    output = {
        "test_1_fullstack": {
            "topic": result1.topic,
            "projects": [
                {
                    "name": p.name,
                    "level": p.level,
                    "tech_stack": p.tech_stack,
                    "github_repo": p.github_guidance.repo_name,
                    "match_score": p.match_score
                }
                for p in result1.projects
            ],
            "youtube_count": len(result1.youtube_project_playlists)
        },
        "test_2_data_science": {
            "topic": result2.topic,
            "projects": [
                {
                    "name": p.name,
                    "level": p.level,
                    "tech_stack": p.tech_stack
                }
                for p in result2.projects
            ]
        }
    }
    
    # Save to file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "project_recommendations_sample.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Detailed output saved to: {output_dir / 'project_recommendations_sample.json'}")
    
    # Test case 3: Mobile App Development
    print("\n" + "="*80)
    print("TEST 3: Mobile App Development Projects")
    print("="*80)
    
    request3 = ProjectRequest(
        topic="Mobile App Development with React Native",
        current_level="intermediate",
        time_available="moderate",
        focus_on_portfolio=True,
        max_projects=3
    )
    
    result3 = await agent.recommend(request3)
    
    print(f"\n📊 Topic: {result3.topic}")
    print(f"💼 Projects: {len(result3.projects)}")
    
    if result3.projects:
        project = result3.projects[0]
        print(f"\nFeatured Project: {project.name}")
        print(f"\n📂 Folder Structure:")
        print(project.github_guidance.folder_structure)
        print(f"\n✨ Professional Practices:")
        for practice in project.github_guidance.professional_practices[:3]:
            print(f"   • {practice}")
        print(f"\n📝 Sample Commit Messages:")
        for msg in project.github_guidance.sample_commit_messages[:3]:
            print(f"   • {msg}")
    
    print("\n" + "="*80)
    print("✅ All tests completed successfully!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_project_recommendations())
