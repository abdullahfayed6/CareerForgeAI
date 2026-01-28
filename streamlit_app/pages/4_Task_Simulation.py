"""
Task Simulation Page
Generate realistic internship task scenarios from top companies.
"""
import streamlit as st

st.set_page_config(
    page_title="Task Simulation | Education Platform",
    page_icon="🏢",
    layout="wide",
)

import sys
sys.path.insert(0, str(__file__).replace("pages/4_Task_Simulation.py", ""))

from utils.styles import inject_css, render_header
from utils.api_client import api_client, APIError

inject_css()


# Sample company suggestions
SAMPLE_COMPANIES = [
    "Instabug",
    "Swvl",
    "Paymob",
    "Vodafone Egypt",
    "Orange Egypt",
    "Microsoft Egypt",
    "Amazon Egypt",
    "Google",
    "Valeo",
    "Si-Ware Systems",
    "Fawry",
    "Dsquares",
    "Robusta",
    "Incorta",
    "Vezeeta",
]

SAMPLE_TASKS = [
    "Build REST API for User Authentication",
    "Implement Search Feature",
    "Design Database Schema for E-commerce",
    "Create CI/CD Pipeline",
    "Build Data Pipeline for Analytics",
    "Implement Caching Layer",
    "Design Microservices Architecture",
    "Build Real-time Notification System",
    "Implement Payment Integration",
    "Create Machine Learning Model Pipeline",
    "Build Mobile App Feature",
    "Design API Rate Limiting",
    "Implement File Upload Service",
    "Create Monitoring Dashboard",
    "Build Message Queue System",
]


def main():
    render_header("🏢 Task Simulation", "Experience real-world internship tasks")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### About Task Simulation")
        st.markdown("""
        Get a realistic preview of what tasks you might work on during an internship at top tech companies.
        
        **Benefits:**
        - Understand real work expectations
        - Practice before your internship
        - Build portfolio projects
        - Develop industry skills
        """)
        
        st.markdown("---")
        st.markdown("### Tips")
        st.markdown("""
        - Choose companies you're interested in
        - Pick tasks related to your skills
        - Try to complete the generated scenarios
        - Add completed tasks to your portfolio!
        """)
    
    # Main content
    st.markdown("### Generate a Task Scenario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Company input with suggestions
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Instabug, Swvl, Google...",
            help="Enter the company name for the task context"
        )
        
        st.markdown("**Popular Companies:**")
        company_cols = st.columns(3)
        for i, company in enumerate(SAMPLE_COMPANIES[:9]):
            with company_cols[i % 3]:
                if st.button(company, key=f"company_{company}", use_container_width=True):
                    st.session_state.selected_company = company
                    st.rerun()
        
        # Check if a company was selected via button
        if "selected_company" in st.session_state and not company_name:
            company_name = st.session_state.selected_company
    
    with col2:
        # Task input with suggestions
        task_title = st.text_input(
            "Task Title",
            placeholder="e.g., Build REST API, Implement Search Feature...",
            help="Enter the task you want to simulate"
        )
        
        st.markdown("**Task Ideas:**")
        task_cols = st.columns(2)
        for i, task in enumerate(SAMPLE_TASKS[:6]):
            with task_cols[i % 2]:
                if st.button(task[:25] + "..." if len(task) > 25 else task, key=f"task_{task}", use_container_width=True):
                    st.session_state.selected_task = task
                    st.rerun()
        
        # Check if a task was selected via button
        if "selected_task" in st.session_state and not task_title:
            task_title = st.session_state.selected_task
    
    # Display current selections
    if company_name or task_title:
        st.markdown("---")
        st.markdown("**Current Selection:**")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏢 Company: {company_name or 'Not selected'}")
        with col2:
            st.info(f"📋 Task: {task_title or 'Not selected'}")
    
    # Generate button
    st.markdown("---")
    
    can_generate = bool(company_name and task_title)
    
    if st.button(
        "🚀 Generate Task Simulation",
        type="primary",
        use_container_width=True,
        disabled=not can_generate
    ):
        with st.spinner(f"Generating task simulation for {company_name}..."):
            try:
                result = api_client.generate_task_simulation(
                    company_name=company_name,
                    task_title=task_title,
                )
                
                st.session_state.task_simulation = result
                st.success("✅ Task simulation generated!")
            
            except APIError as e:
                st.error(f"API Error: {e.message}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if not can_generate:
        st.info("👆 Select both a company and a task to generate a simulation")
    
    # Display simulation result
    if "task_simulation" in st.session_state:
        result = st.session_state.task_simulation
        
        st.markdown("---")
        st.markdown(f"## 🎯 Task Simulation: {result.get('task_title', 'N/A')}")
        st.markdown(f"**Company:** {result.get('company_name', 'N/A')}")
        
        st.markdown("---")
        
        # Display simulation content
        simulation_text = result.get("simulation", "")
        
        if simulation_text:
            # Split into sections if possible
            st.markdown("### 📝 Task Details")
            
            # Display in a nice formatted box
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #e9ecef;">
                <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{simulation_text}</pre>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📥 Download as Text",
                    data=f"Company: {result.get('company_name')}\nTask: {result.get('task_title')}\n\n{simulation_text}",
                    file_name=f"task_simulation_{company_name.replace(' ', '_')}_{task_title.replace(' ', '_')[:20]}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            
            with col2:
                if st.button("🔄 Generate Another", use_container_width=True):
                    if "task_simulation" in st.session_state:
                        del st.session_state.task_simulation
                    if "selected_company" in st.session_state:
                        del st.session_state.selected_company
                    if "selected_task" in st.session_state:
                        del st.session_state.selected_task
                    st.rerun()
            
            with col3:
                st.button("✅ Mark as Completed", use_container_width=True)
        
        # Tips section
        st.markdown("---")
        st.markdown("### 💡 How to Use This Task")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            **Learning Approach:**
            1. Read the task requirements carefully
            2. Break down into smaller subtasks
            3. Research any unfamiliar concepts
            4. Plan your implementation approach
            5. Code incrementally and test often
            """)
        
        with tips_col2:
            st.markdown("""
            **Portfolio Tips:**
            1. Document your solution process
            2. Create a GitHub repository
            3. Write a clear README
            4. Include screenshots/demos
            5. Explain challenges you faced
            """)


if __name__ == "__main__":
    main()
