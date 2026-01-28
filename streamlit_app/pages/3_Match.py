"""
Opportunity Matcher Page
Find internship opportunities that match your profile and skills.
"""
import streamlit as st

st.set_page_config(
    page_title="Opportunity Matcher | Education Platform",
    page_icon="🔍",
    layout="wide",
)

import sys
sys.path.insert(0, str(__file__).replace("pages/3_Match.py", ""))

from utils.styles import inject_css, render_header, render_score_badge
from utils.api_client import api_client, APIError

inject_css()


def render_opportunity_card(opportunity: dict, index: int):
    """Render an opportunity card."""
    score = opportunity.get("score", 0)
    
    # Determine score class
    if score >= 70:
        score_class = "score-excellent"
        score_emoji = "🌟"
    elif score >= 50:
        score_class = "score-good"
        score_emoji = "👍"
    else:
        score_class = "score-fair"
        score_emoji = "📌"
    
    st.markdown(f"""
    <div class="opportunity-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h4 style="margin: 0; color: #333;">{score_emoji} {opportunity.get('title', 'N/A')}</h4>
                <p style="margin: 0.25rem 0; color: #666;">
                    🏢 {opportunity.get('company', 'N/A')} | 📍 {opportunity.get('location', 'N/A')}
                </p>
            </div>
            <span class="opportunity-score {score_class}">{score}/100</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Details & Reasons"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Match Reasons:**")
            for reason in opportunity.get("reasons", []):
                st.markdown(f"✅ {reason}")
        
        with col2:
            st.markdown("**Details:**")
            st.markdown(f"- **Source:** {opportunity.get('source', 'N/A')}")
            st.markdown(f"- **Work Type:** {opportunity.get('work_type', 'N/A')}")
            
            url = opportunity.get("url")
            if url:
                st.markdown(f"[🔗 Apply Now]({url})")


def main():
    render_header("🔍 Opportunity Matcher", "Find internships that match your profile")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### How It Works")
        st.markdown("""
        1. Fill in your academic profile
        2. Add your skills
        3. Set your preferences
        4. Get matched opportunities!
        """)
        
        st.markdown("---")
        st.markdown("### Matching Factors")
        st.markdown("""
        - 🎯 Skills alignment (40%)
        - 📚 Academic level (25%)
        - 📍 Location preference (20%)
        - 📈 Growth potential (15%)
        """)
    
    # Input form
    st.markdown("### Your Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        academic_year = st.selectbox(
            "Academic Year",
            [1, 2, 3, 4, 5],
            index=2,
            help="Your current academic year"
        )
        
        track = st.text_input(
            "Track/Major",
            value="Computer Science",
            help="Your field of study"
        )
        
        preference = st.selectbox(
            "Location Preference",
            ["egypt", "abroad", "remote", "hybrid"],
            index=0,
            help="Your preferred work location"
        )
    
    with col2:
        skills = st.multiselect(
            "Your Skills",
            [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
                "React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "Flask",
                "SQL", "MongoDB", "PostgreSQL", "Redis",
                "AWS", "Azure", "GCP", "Docker", "Kubernetes",
                "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
                "Data Analysis", "Pandas", "NumPy", "TensorFlow", "PyTorch",
                "Git", "Linux", "CI/CD", "REST APIs", "GraphQL",
            ],
            default=["Python", "SQL", "Git"],
            help="Select all skills you have"
        )
        
        notes = st.text_area(
            "Additional Notes (Optional)",
            placeholder="Any specific preferences or requirements...",
            height=100
        )
    
    # Match button
    st.markdown("---")
    
    if st.button("🚀 Find Matching Opportunities", type="primary", use_container_width=True):
        if not skills:
            st.warning("Please select at least one skill.")
            return
        
        with st.spinner("Searching for opportunities and calculating matches..."):
            try:
                result = api_client.match_opportunities(
                    academic_year=academic_year,
                    preference=preference,
                    track=track,
                    skills=skills,
                    notes=notes if notes else None,
                )
                
                st.session_state.match_result = result
                st.success(f"✅ Found {len(result.get('ranked_top5', []))} matching opportunities!")
            
            except APIError as e:
                st.error(f"API Error: {e.message}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display results
    if "match_result" in st.session_state:
        result = st.session_state.match_result
        
        st.markdown("---")
        
        # Profile summary
        profile = result.get("normalized_profile", {})
        if profile:
            with st.expander("📋 Your Normalized Profile"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Year Level:** {profile.get('year_level', 'N/A')}")
                    st.markdown(f"**Track:** {profile.get('track', 'N/A')}")
                with col2:
                    st.markdown(f"**Location Pref:** {profile.get('location_preference', 'N/A')}")
                    st.markdown(f"**Seniority Target:** {profile.get('seniority_target', 'N/A')}")
                with col3:
                    skills_data = profile.get("skills", {})
                    st.markdown("**Skills Breakdown:**")
                    st.markdown(f"- Hard: {', '.join(skills_data.get('hard', []))}")
                    st.markdown(f"- Tools: {', '.join(skills_data.get('tools', []))}")
        
        # Search queries used
        queries = result.get("generated_queries", [])
        if queries:
            with st.expander("🔎 Search Queries Used"):
                for q in queries:
                    st.markdown(f"- **{q.get('provider', 'N/A')}:** {q.get('query', 'N/A')}")
                    st.caption(q.get('rationale', ''))
        
        # Top opportunities
        st.markdown("### 🏆 Top Matched Opportunities")
        
        ranked = result.get("ranked_top5", [])
        
        if ranked:
            # Sorting options
            col1, col2 = st.columns([2, 1])
            with col2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Score (High to Low)", "Score (Low to High)", "Company A-Z"],
                    key="sort_opportunities"
                )
            
            # Sort opportunities
            if sort_by == "Score (High to Low)":
                ranked = sorted(ranked, key=lambda x: x.get("score", 0), reverse=True)
            elif sort_by == "Score (Low to High)":
                ranked = sorted(ranked, key=lambda x: x.get("score", 0))
            elif sort_by == "Company A-Z":
                ranked = sorted(ranked, key=lambda x: x.get("company", "").lower())
            
            for i, opp in enumerate(ranked, 1):
                render_opportunity_card(opp, i)
        else:
            st.info("No opportunities found. Try adjusting your skills or preferences.")
        
        # All opportunities
        all_opps = result.get("opportunities_top20", [])
        if all_opps:
            with st.expander(f"📋 All Fetched Opportunities ({len(all_opps)})"):
                for opp in all_opps:
                    st.markdown(f"""
                    - **{opp.get('title', 'N/A')}** at {opp.get('company', 'N/A')} 
                      ({opp.get('location', 'N/A')}) - [{opp.get('source', 'N/A')}]
                    """)


if __name__ == "__main__":
    main()
