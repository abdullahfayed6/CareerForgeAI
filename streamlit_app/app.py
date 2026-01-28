"""
Education Platform - Multi-Agent System
Main Streamlit Application
"""
import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Education Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_css, render_header
from utils.api_client import api_client

# Inject custom CSS
inject_css()


def main():
    """Main application entry point."""
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/graduation-cap.png", width=80)
        st.title("Education Platform")
        st.markdown("---")
        
        # API Health Check
        if api_client.health_check():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info("Make sure the FastAPI server is running on http://localhost:8000")
        
        st.markdown("---")
        st.markdown("### Navigation")
        st.markdown("""
        - 📝 **Interview** - Practice interviews
        - 🎯 **Career** - Translate lectures
        - 🔍 **Match** - Find opportunities
        - 🏢 **Tasks** - Simulate work tasks
        """)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This platform uses AI agents to help you:
        - Practice for technical interviews
        - Understand career value of your courses
        - Find matching internship opportunities
        - Experience real-world tasks
        """)
    
    # Main content
    render_header(
        "🎓 Education Platform",
        "Your AI-powered career development companion"
    )
    
    # Welcome section
    st.markdown("## Welcome!")
    st.markdown("""
    This multi-agent system provides four powerful services to accelerate your career journey.
    Select a service from the sidebar navigation or explore the options below.
    """)
    
    # Service cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Interview System")
        st.markdown("""
        Practice adaptive technical and behavioral interviews with real-time evaluation.
        
        **Features:**
        - 7 specialized AI agents
        - Real-time difficulty adjustment
        - Comprehensive feedback
        - Final performance report
        """)
        if st.button("Start Interview →", key="nav_interview"):
            st.switch_page("pages/1_Interview.py")
        
        st.markdown("---")
        
        st.markdown("### 🔍 Opportunity Matcher")
        st.markdown("""
        Find internship opportunities that match your profile and skills.
        
        **Features:**
        - AI-powered matching
        - Personalized recommendations
        - Score-based ranking
        - Detailed match reasons
        """)
        if st.button("Find Opportunities →", key="nav_match"):
            st.switch_page("pages/3_Match.py")
    
    with col2:
        st.markdown("### 🎯 Career Translator")
        st.markdown("""
        Convert academic lectures into industry-relevant skills and tasks.
        
        **Features:**
        - Real-world use cases
        - Company-style tasks
        - Skills mapping
        - Career impact analysis
        """)
        if st.button("Translate Lecture →", key="nav_career"):
            st.switch_page("pages/2_Career.py")
        
        st.markdown("---")
        
        st.markdown("### 🏢 Task Simulation")
        st.markdown("""
        Experience realistic internship task scenarios from top companies.
        
        **Features:**
        - Real company contexts
        - Practical challenges
        - Industry-standard tasks
        - Skill development focus
        """)
        if st.button("Generate Task →", key="nav_task"):
            st.switch_page("pages/4_Task_Simulation.py")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made with ❤️ for students | Powered by AI Agents"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
