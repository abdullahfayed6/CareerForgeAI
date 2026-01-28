"""Custom CSS styles for the Streamlit app."""

MAIN_CSS = """
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Card styling */
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .error-card {
        background: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    
    /* Score display */
    .score-display {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
    }
    
    .score-high {
        color: #28a745;
    }
    
    .score-medium {
        color: #ffc107;
    }
    
    .score-low {
        color: #dc3545;
    }
    
    /* Chat styling */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .chat-question {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .chat-answer {
        background: #f5f5f5;
        border-left: 4px solid #9e9e9e;
    }
    
    /* Opportunity card */
    .opportunity-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .opportunity-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .opportunity-score {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .score-excellent {
        background: #d4edda;
        color: #155724;
    }
    
    .score-good {
        background: #fff3cd;
        color: #856404;
    }
    
    .score-fair {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Progress indicator */
    .progress-step {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .step-active {
        background: #667eea;
        color: white;
    }
    
    .step-completed {
        background: #28a745;
        color: white;
    }
    
    .step-pending {
        background: #e9ecef;
        color: #6c757d;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd6 0%, #6a4190 100%);
    }
    
    /* Metric styling */
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(MAIN_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Render a styled header."""
    import streamlit as st
    header_html = f"""
    <div class="main-header">
        <h1>{title}</h1>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_info_card(content: str):
    """Render an info card."""
    import streamlit as st
    st.markdown(f'<div class="info-card">{content}</div>', unsafe_allow_html=True)


def render_success_card(content: str):
    """Render a success card."""
    import streamlit as st
    st.markdown(f'<div class="success-card">{content}</div>', unsafe_allow_html=True)


def render_score_badge(score: int) -> str:
    """Return HTML for a score badge."""
    if score >= 70:
        css_class = "score-excellent"
    elif score >= 50:
        css_class = "score-good"
    else:
        css_class = "score-fair"
    return f'<span class="opportunity-score {css_class}">{score}/100</span>'
