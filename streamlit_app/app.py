"""
Main Streamlit application for the content rating system.
"""
import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# Configure page settings
st.set_page_config(
    page_title="Content Rating System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000/api/v1"

def create_radar_chart(scores):
    """Create a radar chart for rating scores."""
    categories = list(scores.keys())
    values = list(scores.values())
    values.append(values[0])  # Complete the polygon
    categories.append(categories[0])  # Complete the polygon
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color='#4CAF50')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title="Rating Breakdown"
    )
    return fig

def display_metrics(rating_response):
    """Display rating metrics in a grid."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Final Score", f"{rating_response['final_score']:.2f}/10")
    
    with col2:
        highest_score = max(rating_response['scores'].items(), key=lambda x: x[1])
        st.metric("Highest Score", f"{highest_score[0]}: {highest_score[1]:.2f}")
    
    with col3:
        st.metric("Resource ID", rating_response['resource_id'][:8])

def main():
    """Main application function."""
    st.title("Content Rating System")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Select a page",
        ["Single Rating", "Batch Rating", "Analytics"]
    )
    
    if page == "Single Rating":
        st.header("Rate Single Content")
        
        with st.form("rating_form"):
            title = st.text_input("Content Title")
            content = st.text_area("Content")
            author = st.text_input("Author")
            url = st.text_input("URL")
            
            # Metadata inputs
            st.subheader("Metadata")
            col1, col2 = st.columns(2)
            
            with col1:
                keywords = st.text_input("Keywords (comma-separated)")
                category = st.text_input("Category")
                view_count = st.number_input("View Count", min_value=0)
                social_shares = st.number_input("Social Shares", min_value=0)
            
            with col2:
                author_score = st.slider("Author Expertise (0-10)", 0.0, 10.0, 5.0)
                domain_authority = st.slider("Domain Authority (0-100)", 0.0, 100.0, 50.0)
                user_satisfaction = st.slider("User Satisfaction (0-10)", 0.0, 10.0, 5.0)
                
            submitted = st.form_submit_button("Rate Content")
            
            if submitted:
                try:
                    # Prepare request data
                    data = {
                        "title": title,
                        "content": content,
                        "author": author,
                        "url": url,
                        "publication_date": datetime.now().isoformat(),
                        "metadata": {
                            "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                            "category": category,
                            "language": "en",
                            "view_count": view_count,
                            "avg_interaction_time": 0,
                            "social_shares": social_shares,
                            "total_interactions": view_count,
                            "citations": 0,
                            "author_credentials_score": author_score,
                            "domain_authority": domain_authority,
                            "positive_outcomes": 0,
                            "conversion_rate": 0.0,
                            "user_satisfaction": user_satisfaction,
                            "review_count": 0
                        }
                    }
                    
                    # Make API request
                    response = requests.post(f"{API_URL}/rate", json=data)
                    response.raise_for_status()
                    rating = response.json()
                    
                    # Display results
                    st.success("Content rated successfully!")
                    display_metrics(rating)
                    
                    # Display radar chart
                    fig = create_radar_chart(rating['scores'])
                    st.plotly_chart(fig)
                    
                    # Display detailed results
                    with st.expander("View Detailed Results"):
                        st.json(rating)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    elif page == "Batch Rating":
        st.header("Batch Content Rating")
        
        uploaded_file = st.file_uploader(
            "Upload JSON file with content items",
            type=['json'],
            help="File should contain an array of content items"
        )
        
        if uploaded_file:
            try:
                contents = json.load(uploaded_file)
                st.info(f"Loaded {len(contents)} items")
                
                if st.button("Process Batch"):
                    with st.spinner("Processing batch..."):
                        response = requests.post(
                            f"{API_URL}/rate-batch",
                            json={"resources": contents}
                        )
                        response.raise_for_status()
                        results = response.json()
                        
                        st.success(f"Processed {results['total_processed']} items")
                        
                        # Display results table
                        df = pd.DataFrame([
                            {
                                'Title': r['title'],
                                'Final Score': r['final_score'],
                                'Resource ID': r['resource_id'][:8]
                            }
                            for r in results['results']
                        ])
                        st.dataframe(df)
                        
                        # Download results
                        st.download_button(
                            "Download Results",
                            data=json.dumps(results, indent=2),
                            file_name="batch_results.json",
                            mime="application/json"
                        )
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    else:  # Analytics page
        st.header("System Analytics")
        
        try:
            response = requests.get(f"{API_URL}/stats")
            response.raise_for_status()
            stats = response.json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ratings", stats['total_ratings'])
            
            with col2:
                st.metric(
                    "Average Processing Time",
                    f"{stats['avg_processing_time']:.2f}s"
                )
            
            with col3:
                st.metric(
                    "Cache Size",
                    f"{stats['cache_stats']['current_size_bytes'] / 1024:.1f}KB"
                )
            
            # Cache usage chart
            cache_data = stats['cache_stats']
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Used', 'Available'],
                    values=[
                        cache_data['current_size_bytes'],
                        cache_data['max_size_bytes'] - cache_data['current_size_bytes']
                    ],
                    hole=.3
                )
            ])
            fig.update_layout(title="Cache Usage")
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"Error fetching analytics: {str(e)}")

if __name__ == "__main__":
    main()
