"""Project Recommender Page - Build Portfolio-Ready Projects."""
import streamlit as st
from typing import Dict, Any
from streamlit_app.utils.api_client import api_client, APIError
from streamlit_app.utils.styles import apply_custom_styles

# Page config
st.set_page_config(
    page_title="Project Builder",
    page_icon="💼",
    layout="wide",
)

apply_custom_styles()

# Header
st.title("💼 Practical Project Recommender")
st.markdown("""
**Transform learning into building.** Get hands-on, portfolio-ready projects with professional 
GitHub structuring guidance and YouTube tutorials.
""")

# Sidebar - Input Form
with st.sidebar:
    st.header("🎯 Project Settings")
    
    topic = st.text_input(
        "Topic / Field",
        placeholder="e.g., Full-Stack Web Development",
        help="What topic do you want to build projects for?"
    )
    
    current_level = st.selectbox(
        "Your Current Level",
        ["beginner", "intermediate", "advanced"],
        index=1,
        help="Your current skill level in this topic"
    )
    
    time_available = st.selectbox(
        "Time Available",
        ["limited", "moderate", "extensive"],
        index=1,
        help="How much time you can dedicate to projects"
    )
    
    max_projects = st.slider(
        "Number of Projects",
        min_value=3,
        max_value=10,
        value=5,
        help="Maximum projects to recommend"
    )
    
    focus_on_portfolio = st.checkbox(
        "Focus on Portfolio Quality",
        value=True,
        help="Prioritize projects that are impressive for portfolios"
    )
    
    generate_btn = st.button("🚀 Generate Projects", type="primary", use_container_width=True)

# Initialize session state
if 'project_results' not in st.session_state:
    st.session_state.project_results = None
if 'loading' not in st.session_state:
    st.session_state.loading = False

# Generate recommendations
if generate_btn:
    if not topic:
        st.error("⚠️ Please enter a topic or field!")
    else:
        st.session_state.loading = True
        
        with st.spinner("🔍 Generating practical projects and resources..."):
            try:
                results = api_client.get_project_recommendations(
                    topic=topic,
                    current_level=current_level,
                    time_available=time_available,
                    focus_on_portfolio=focus_on_portfolio,
                    max_projects=max_projects,
                )
                st.session_state.project_results = results
                st.session_state.loading = False
                st.success("✅ Projects generated successfully!")
            except APIError as e:
                st.error(f"❌ Error: {e.message}")
                st.session_state.loading = False
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.session_state.loading = False

# Display Results
if st.session_state.project_results:
    results = st.session_state.project_results
    
    # Topic Summary
    st.markdown("---")
    st.subheader(f"📊 {results.get('topic', 'Projects')}")
    st.info(results.get('topic_summary', 'Building practical projects...'))
    
    # Projects Section
    st.markdown("---")
    st.header("💼 Recommended Projects")
    
    projects = results.get('projects', [])
    
    if projects:
        # Group projects by level
        beginner = [p for p in projects if p.get('level') == 'beginner']
        intermediate = [p for p in projects if p.get('level') == 'intermediate']
        advanced = [p for p in projects if p.get('level') == 'advanced']
        
        # Display by level
        for level_name, level_projects in [
            ("🟢 Beginner Projects", beginner),
            ("🟡 Intermediate Projects", intermediate),
            ("🔴 Advanced Projects", advanced)
        ]:
            if level_projects:
                st.markdown(f"### {level_name}")
                
                for idx, project in enumerate(level_projects):
                    with st.expander(
                        f"{project.get('icon', '💼')} **{project.get('name', 'Project')}** "
                        f"(Match: {project.get('match_score', 0)}%)",
                        expanded=(idx == 0)
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Description:** {project.get('description', '')}")
                            st.markdown(f"**What You'll Build:**")
                            st.write(project.get('what_you_will_build', ''))
                            
                            st.markdown("**🎯 Skills Gained:**")
                            for skill in project.get('skills_gained', [])[:5]:
                                st.markdown(f"- {skill}")
                            
                            st.markdown("**💡 Real-World Connection:**")
                            st.write(project.get('real_work_connection', ''))
                            
                            st.markdown("**📈 CV Value:**")
                            st.write(project.get('cv_value', ''))
                        
                        with col2:
                            st.markdown("**⏱️ Duration:**")
                            st.info(project.get('estimated_duration', 'N/A'))
                            
                            st.markdown("**🏢 Relevant Roles:**")
                            for role in project.get('relevant_roles', [])[:3]:
                                st.markdown(f"- {role}")
                            
                            st.markdown("**🛠️ Tech Stack:**")
                            for tech in project.get('tech_stack', []):
                                st.markdown(f"- {tech}")
                        
                        # GitHub Guidance
                        github = project.get('github_guidance', {})
                        if github:
                            st.markdown("---")
                            st.markdown("### 📂 GitHub Repository Guidance")
                            
                            tab1, tab2, tab3, tab4 = st.tabs([
                                "📁 Structure",
                                "📝 README",
                                "✅ Best Practices",
                                "💬 Commits"
                            ])
                            
                            with tab1:
                                st.markdown(f"**Repository Name:** `{github.get('repo_name', 'project')}`")
                                st.markdown("**Folder Structure:**")
                                st.code(github.get('folder_structure', ''), language='text')
                            
                            with tab2:
                                st.markdown("**README Should Contain:**")
                                for item in github.get('readme_should_contain', []):
                                    st.markdown(f"- {item}")
                            
                            with tab3:
                                st.markdown("**Professional Practices:**")
                                for practice in github.get('professional_practices', []):
                                    st.markdown(f"✓ {practice}")
                            
                            with tab4:
                                st.markdown("**Sample Commit Messages:**")
                                for commit in github.get('sample_commit_messages', []):
                                    st.code(commit, language='text')
    else:
        st.warning("No projects found. Try adjusting your criteria.")
    
    # YouTube Playlists Section
    st.markdown("---")
    st.header("🎬 YouTube Project Tutorials")
    
    playlists = results.get('youtube_project_playlists', [])
    
    if playlists:
        for playlist in playlists:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {playlist.get('icon', '🎬')} {playlist.get('title', 'Tutorial')}")
                    st.markdown(f"**Focus:** {playlist.get('focus', '')}")
                    st.markdown(f"**Channel:** {playlist.get('channel', 'Unknown')}")
                    
                    url = playlist.get('url', '')
                    if url:
                        st.markdown(f"[🔗 Watch Playlist]({url})")
                
                with col2:
                    level = playlist.get('level', 'intermediate')
                    level_emoji = {
                        'beginner': '🟢',
                        'intermediate': '🟡',
                        'advanced': '🔴'
                    }.get(level, '⚪')
                    
                    st.metric("Level", f"{level_emoji} {level.title()}")
                    st.metric("Duration", playlist.get('duration', 'N/A'))
                
                st.markdown("---")
    else:
        st.info("No YouTube playlists available.")
    
    # Additional Guidance
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 Why Build Projects?")
        why_build = results.get('why_build_projects', [])
        if why_build:
            for reason in why_build:
                st.markdown(f"✓ {reason}")
    
    with col2:
        st.markdown("### 📋 Portfolio Tips")
        tips = results.get('portfolio_tips', [])
        if tips:
            for tip in tips:
                st.markdown(f"💡 {tip}")
    
    # Next Steps
    st.markdown("---")
    st.markdown("### 🚀 Next Steps")
    next_steps = results.get('next_steps', [])
    if next_steps:
        for step in next_steps:
            st.markdown(f"→ {step}")
    
    # Download as JSON
    st.markdown("---")
    import json
    json_data = json.dumps(results, indent=2)
    st.download_button(
        label="📥 Download Full Recommendations (JSON)",
        data=json_data,
        file_name=f"project_recommendations_{topic.replace(' ', '_').lower()}.json",
        mime="application/json"
    )

else:
    # Welcome / Instructions
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 What You Get
        - **Beginner → Advanced Projects**
        - **Complete GitHub Guidance**
        - **Professional Structuring**
        - **YouTube Tutorials**
        """)
    
    with col2:
        st.markdown("""
        ### 💼 For Your Portfolio
        - **Industry-Ready Projects**
        - **Real-World Applications**
        - **Employability Focus**
        - **Interview Material**
        """)
    
    with col3:
        st.markdown("""
        ### 📚 Learn by Building
        - **Hands-On Practice**
        - **Step-by-Step Guides**
        - **Best Practices**
        - **Career-Focused**
        """)
    
    st.info("👈 Enter a topic in the sidebar to get started!")

# Footer
st.markdown("---")
st.caption("💼 Practical Project Recommender - Transform learning into building")
