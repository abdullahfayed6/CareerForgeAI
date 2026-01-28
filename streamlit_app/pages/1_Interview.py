"""
Interview System Page
Adaptive technical and behavioral interviews with real-time evaluation.
"""
import streamlit as st
import uuid
from datetime import datetime

st.set_page_config(
    page_title="Interview System | Education Platform",
    page_icon="📝",
    layout="wide",
)

import sys
sys.path.insert(0, str(__file__).replace("pages/1_Interview.py", ""))

from utils.styles import inject_css, render_header
from utils.api_client import api_client, APIError

inject_css()

# Initialize session state
if "interview_session_id" not in st.session_state:
    st.session_state.interview_session_id = None
if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "interview_state" not in st.session_state:
    st.session_state.interview_state = "INTRO"
if "interview_difficulty" not in st.session_state:
    st.session_state.interview_difficulty = 3
if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []


def reset_interview():
    """Reset interview session state."""
    st.session_state.interview_session_id = None
    st.session_state.interview_messages = []
    st.session_state.current_question = None
    st.session_state.interview_state = "INTRO"
    st.session_state.interview_difficulty = 3
    st.session_state.interview_complete = False
    st.session_state.evaluations = []


def render_interview_progress():
    """Render interview progress indicator."""
    states = ["INTRO", "WARMUP", "CORE_QUESTIONS", "PRESSURE_ROUND", "COMMUNICATION_TEST", "CLOSING", "FEEDBACK"]
    current_state = st.session_state.interview_state
    
    progress_html = ""
    for state in states:
        if state == current_state:
            css_class = "step-active"
        elif states.index(state) < states.index(current_state):
            css_class = "step-completed"
        else:
            css_class = "step-pending"
        
        display_name = state.replace("_", " ").title()
        progress_html += f'<span class="progress-step {css_class}">{display_name}</span>'
    
    st.markdown(f'<div style="margin-bottom: 1rem;">{progress_html}</div>', unsafe_allow_html=True)


def render_evaluation_metrics(evaluation: dict):
    """Render evaluation metrics."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Technical", f"{evaluation.get('technical_score', 0)}/5")
    with col2:
        st.metric("Reasoning", f"{evaluation.get('reasoning_depth', 0)}/5")
    with col3:
        st.metric("Clarity", f"{evaluation.get('communication_clarity', 0)}/5")
    with col4:
        st.metric("Structure", f"{evaluation.get('structure_score', 0)}/5")
    with col5:
        st.metric("Confidence", f"{evaluation.get('confidence_signals', 0)}/5")


def main():
    render_header("📝 Interview System", "Practice with AI-powered adaptive interviews")
    
    # Sidebar with session info
    with st.sidebar:
        st.markdown("### Interview Status")
        if st.session_state.interview_session_id:
            st.success(f"Session Active")
            st.info(f"State: {st.session_state.interview_state}")
            st.info(f"Difficulty: {st.session_state.interview_difficulty}/5")
            
            if st.button("🔄 New Interview", use_container_width=True):
                reset_interview()
                st.rerun()
        else:
            st.info("No active session")
        
        if st.session_state.evaluations:
            st.markdown("### Performance")
            avg_score = sum(
                (e.get("technical_score", 0) + e.get("reasoning_depth", 0) + 
                 e.get("communication_clarity", 0) + e.get("structure_score", 0) + 
                 e.get("confidence_signals", 0)) / 5
                for e in st.session_state.evaluations
            ) / len(st.session_state.evaluations)
            st.metric("Average Score", f"{avg_score:.1f}/5")
    
    # Main content
    if not st.session_state.interview_session_id:
        # Configuration form
        st.markdown("### Configure Your Interview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_role = st.text_input(
                "Target Role",
                value="Backend Engineer",
                help="e.g., Backend Engineer, Data Scientist, ML Engineer"
            )
            
            experience_level = st.selectbox(
                "Experience Level",
                ["Junior", "Mid", "Senior", "Expert"],
                index=0
            )
            
            company_type = st.selectbox(
                "Company Type",
                ["FAANG", "Startup", "Enterprise", "Consulting", "Agency"],
                index=1
            )
            
            interview_type = st.selectbox(
                "Interview Type",
                ["Technical", "Behavioral", "Communication", "Mixed"],
                index=3
            )
        
        with col2:
            difficulty = st.slider(
                "Initial Difficulty",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Easy, 5 = Hard"
            )
            
            tech_stack = st.multiselect(
                "Tech Stack",
                ["Python", "JavaScript", "TypeScript", "Java", "Go", "SQL", "AWS", "Docker", "Kubernetes", "React", "Node.js"],
                default=["Python", "SQL"]
            )
            
            focus_area = st.text_input(
                "Focus Area",
                value="General",
                help="e.g., System Design, Algorithms, API Design"
            )
            
            communication_strictness = st.slider(
                "Communication Strictness",
                min_value=1,
                max_value=5,
                value=3
            )
        
        # Start button
        st.markdown("---")
        
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            with st.spinner("Starting interview session..."):
                try:
                    config = {
                        "target_role": target_role,
                        "experience_level": experience_level,
                        "company_type": company_type,
                        "interview_type": interview_type,
                        "difficulty": difficulty,
                        "tech_stack": tech_stack,
                        "focus_area": focus_area,
                        "communication_strictness": communication_strictness,
                        "allow_coding": False,
                        "scale": "Medium",
                        "leadership_level": "None",
                        "focus_traits": ["Problem Solving", "Communication"],
                        "allow_interruptions": False,
                        "time_pressure": False,
                    }
                    
                    result = api_client.start_interview(
                        user_id=str(uuid.uuid4()),
                        config=config,
                    )
                    
                    st.session_state.interview_session_id = result["session_id"]
                    st.session_state.current_question = result["first_question"]
                    st.session_state.interview_state = result.get("state", "INTRO")
                    st.session_state.interview_difficulty = result.get("difficulty", difficulty)
                    
                    st.session_state.interview_messages.append({
                        "role": "interviewer",
                        "content": result["first_question"],
                        "timestamp": datetime.now().isoformat(),
                    })
                    
                    st.success("Interview started! Good luck! 🎯")
                    st.rerun()
                
                except APIError as e:
                    st.error(f"Failed to start interview: {e.message}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    else:
        # Active interview session
        render_interview_progress()
        
        if st.session_state.interview_complete:
            st.success("🎉 Interview Complete!")
            
            # Show final report button
            if st.button("📊 View Final Report", type="primary"):
                with st.spinner("Generating report..."):
                    try:
                        report = api_client.get_final_report(st.session_state.interview_session_id)
                        
                        st.markdown("### Final Interview Report")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Score", f"{report.get('overall_score', 0):.1f}/5")
                        with col2:
                            st.info(f"**Technical Level:** {report.get('technical_level_estimate', 'N/A')}")
                        with col3:
                            st.info(f"**Communication:** {report.get('communication_profile', 'N/A')}")
                        
                        st.markdown("#### Strengths")
                        for strength in report.get("strengths", []):
                            st.markdown(f"✅ {strength}")
                        
                        st.markdown("#### Areas for Improvement")
                        for weakness in report.get("weaknesses", []):
                            st.markdown(f"⚠️ {weakness}")
                        
                        st.markdown("#### Improvement Plan")
                        st.write(report.get("improvement_plan", "N/A"))
                        
                        if report.get("hiring_risks"):
                            st.markdown("#### Hiring Risks")
                            for risk in report.get("hiring_risks", []):
                                st.warning(risk)
                    
                    except APIError as e:
                        st.error(f"Failed to get report: {e.message}")
            
            if st.button("Start New Interview"):
                reset_interview()
                st.rerun()
        
        else:
            # Display conversation history
            st.markdown("### Interview Conversation")
            
            chat_container = st.container()
            
            with chat_container:
                for msg in st.session_state.interview_messages:
                    if msg["role"] == "interviewer":
                        st.markdown(f"""
                        <div class="chat-message chat-question">
                            <strong>🤖 Interviewer:</strong><br>
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message chat-answer">
                            <strong>👤 You:</strong><br>
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show evaluation if available
                        if "evaluation" in msg:
                            with st.expander("📊 Evaluation"):
                                render_evaluation_metrics(msg["evaluation"])
                                if msg["evaluation"].get("feedback"):
                                    st.info(f"**Feedback:** {msg['evaluation']['feedback']}")
            
            # Answer input
            st.markdown("---")
            st.markdown("### Your Answer")
            
            answer = st.text_area(
                "Type your answer here",
                height=150,
                placeholder="Take your time to think through your answer...",
                key="answer_input"
            )
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button("📤 Submit Answer", type="primary", use_container_width=True, disabled=not answer):
                    with st.spinner("Evaluating your answer..."):
                        try:
                            result = api_client.submit_answer(
                                session_id=st.session_state.interview_session_id,
                                question=st.session_state.current_question,
                                answer=answer,
                            )
                            
                            # Add answer to messages
                            st.session_state.interview_messages.append({
                                "role": "candidate",
                                "content": answer,
                                "timestamp": datetime.now().isoformat(),
                                "evaluation": result.get("evaluation", {}),
                            })
                            
                            # Store evaluation
                            st.session_state.evaluations.append(result.get("evaluation", {}))
                            
                            # Update state
                            st.session_state.interview_state = result.get("next_state", st.session_state.interview_state)
                            st.session_state.interview_difficulty = result.get("difficulty_adjustment", {}).get("new_difficulty", st.session_state.interview_difficulty)
                            
                            if result.get("is_complete"):
                                st.session_state.interview_complete = True
                            elif result.get("next_question"):
                                st.session_state.current_question = result["next_question"]
                                st.session_state.interview_messages.append({
                                    "role": "interviewer",
                                    "content": result["next_question"],
                                    "timestamp": datetime.now().isoformat(),
                                })
                            
                            st.rerun()
                        
                        except APIError as e:
                            st.error(f"Failed to submit answer: {e.message}")
            
            with col2:
                if st.button("⏭️ Skip Question", use_container_width=True):
                    st.warning("Skipping is not recommended. Try your best!")


if __name__ == "__main__":
    main()
