"""
Career Translator Page
Convert academic lectures into industry-relevant skills and tasks.
"""
import streamlit as st
import json

st.set_page_config(
    page_title="Career Translator | Education Platform",
    page_icon="🎯",
    layout="wide",
)

import sys
sys.path.insert(0, str(__file__).replace("pages/2_Career.py", ""))

from utils.styles import inject_css, render_header
from utils.api_client import api_client, APIError

inject_css()


def render_use_case_card(use_case: dict):
    """Render an industry use case card."""
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #667eea;">
        <strong>🏢 {use_case.get('domain', 'N/A')}</strong><br>
        <em>{use_case.get('scenario', 'N/A')}</em><br>
        <small style="color: #666;">How it's used: {use_case.get('how_concept_is_used', 'N/A')}</small>
    </div>
    """, unsafe_allow_html=True)


def render_task_card(task: dict):
    """Render a company-style task card."""
    st.markdown(f"""
    <div style="background: #e8f5e9; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #4caf50;">
        <strong>📋 {task.get('task_title', 'N/A')}</strong><br>
        <em style="color: #666;">{task.get('company_context', 'N/A')}</em><br>
        <p><strong>Your Mission:</strong> {task.get('your_mission', 'N/A')}</p>
        <p><strong>Expected Output:</strong> {task.get('expected_output', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if task.get('constraints'):
        with st.expander("⚠️ Constraints"):
            for constraint in task.get('constraints', []):
                st.markdown(f"- {constraint}")


def main():
    render_header("🎯 Career Translator", "Transform academic knowledge into industry value")
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### How It Works")
        st.markdown("""
        1. Enter your lecture topic
        2. Optionally add lecture notes
        3. Select your target career track
        4. Get industry-relevant insights!
        """)
        
        st.markdown("---")
        st.markdown("### Output Includes")
        st.markdown("""
        - 🌍 Real-world relevance
        - 🏢 Industry use cases
        - 📋 Company-style tasks
        - 💼 Career impact
        - 🎯 Skills developed
        """)
    
    # Input form
    st.markdown("### Enter Lecture Details")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        lecture_topic = st.text_input(
            "Lecture Topic *",
            placeholder="e.g., Binary Search Trees, Neural Networks, REST APIs",
            help="Enter the main topic of your lecture"
        )
        
        lecture_text = st.text_area(
            "Lecture Notes (Optional)",
            height=150,
            placeholder="Paste your lecture notes, slides content, or key concepts here...",
            help="Adding more context helps generate better insights"
        )
    
    with col2:
        target_track = st.selectbox(
            "Target Career Track",
            [
                "Software Engineer",
                "Backend Developer",
                "Frontend Developer",
                "Full Stack Developer",
                "Data Scientist",
                "ML Engineer",
                "DevOps Engineer",
                "Cloud Architect",
                "Data Engineer",
                "Security Engineer",
            ],
            help="Select your target career path"
        )
        
        st.markdown("---")
        st.info("💡 Tip: Be specific with your topic for better results!")
    
    # Translate button
    st.markdown("---")
    
    if st.button("🚀 Translate to Career Value", type="primary", use_container_width=True, disabled=not lecture_topic):
        with st.spinner("Analyzing lecture and generating career insights..."):
            try:
                result = api_client.translate_lecture(
                    lecture_topic=lecture_topic,
                    lecture_text=lecture_text if lecture_text else None,
                    target_track=target_track,
                )
                
                if result.get("success") and result.get("data"):
                    translation = result["data"]
                    st.session_state.translation_result = translation
                    st.success("✅ Translation complete!")
                else:
                    st.error("Translation failed. Please try again.")
            
            except APIError as e:
                st.error(f"API Error: {e.message}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display results
    if "translation_result" in st.session_state:
        translation = st.session_state.translation_result
        
        st.markdown("---")
        st.markdown(f"## 📚 {translation.get('lecture_topic', lecture_topic)}")
        
        # Tabs for different sections
        tabs = st.tabs([
            "🌍 Real-World Relevance",
            "🏢 Industry Use Cases",
            "📋 Practical Tasks",
            "💼 Career Impact",
            "🎯 Skills Built",
            "🔥 Challenges",
        ])
        
        # Real-World Relevance Tab
        with tabs[0]:
            relevance = translation.get("real_world_relevance", {})
            
            st.markdown("### Where This Is Used")
            for item in relevance.get("where_used", []):
                st.markdown(f"✅ {item}")
            
            st.markdown("### Problems It Solves")
            for item in relevance.get("problems_it_solves", []):
                st.markdown(f"🔧 {item}")
            
            if relevance.get("risk_if_not_known"):
                st.warning(f"⚠️ **Risk if not known:** {relevance.get('risk_if_not_known')}")
        
        # Industry Use Cases Tab
        with tabs[1]:
            st.markdown("### How Companies Use This")
            use_cases = translation.get("industry_use_cases", [])
            
            for use_case in use_cases:
                render_use_case_card(use_case)
        
        # Practical Tasks Tab
        with tabs[2]:
            st.markdown("### Try These Company-Style Tasks")
            tasks = translation.get("company_style_tasks", [])
            
            for i, task in enumerate(tasks, 1):
                st.markdown(f"#### Task {i}")
                render_task_card(task)
        
        # Career Impact Tab
        with tabs[3]:
            impact = translation.get("career_impact", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Relevant Roles")
                for role in impact.get("relevant_roles", []):
                    st.markdown(f"👔 {role}")
            
            with col2:
                st.markdown("### Interview Relevance")
                st.info(impact.get("interview_relevance", "N/A"))
            
            st.markdown("### Junior vs Senior Difference")
            st.markdown(impact.get("junior_vs_senior_difference", "N/A"))
        
        # Skills Built Tab
        with tabs[4]:
            skills = translation.get("skills_built", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Technical Skills")
                for skill in skills.get("technical", []):
                    st.markdown(f"💻 {skill}")
                
                st.markdown("### Problem Solving")
                for skill in skills.get("problem_solving", []):
                    st.markdown(f"🧩 {skill}")
            
            with col2:
                st.markdown("### Engineering Thinking")
                for skill in skills.get("engineering_thinking", []):
                    st.markdown(f"🔧 {skill}")
                
                st.markdown("### Team Relevance")
                for skill in skills.get("team_relevance", []):
                    st.markdown(f"🤝 {skill}")
        
        # Challenges Tab
        with tabs[5]:
            st.markdown("### Advanced Challenges")
            challenges = translation.get("advanced_challenges", [])
            
            for challenge in challenges:
                with st.expander(f"🎯 {challenge.get('title', 'Challenge')}"):
                    st.write(challenge.get("description", "N/A"))
            
            st.markdown("### Production Challenges")
            prod_challenges = translation.get("production_challenges", [])
            
            for pc in prod_challenges:
                st.markdown(f"""
                <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #ff9800;">
                    <strong>⚠️ {pc.get('challenge', 'N/A')}</strong><br>
                    <p><strong>Why it happens:</strong> {pc.get('why_it_happens', 'N/A')}</p>
                    <p><strong>Solution:</strong> {pc.get('professional_solution', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Download option
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.download_button(
                "📥 Download as JSON",
                data=json.dumps(translation, indent=2),
                file_name=f"career_translation_{lecture_topic.replace(' ', '_')}.json",
                mime="application/json",
            )


if __name__ == "__main__":
    main()
