"""
Main Streamlit application for the content rating system.
"""
import streamlit as st
import requests
import json
import base64
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
    .upload-section {
        border: 2px dashed #ccc;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .file-info {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000/api/v1"

def create_radar_chart(scores):
    """Create a radar chart for rating scores."""
    categories = list(scores.keys())
    values = list(scores.values())
    values.append(values[0])
    categories.append(categories[0])
    
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

def get_file_content(uploaded_file):
    """Process uploaded file and return content in appropriate format."""
    file_type = None
    content = None
    mime_type = uploaded_file.type

    if mime_type == "application/pdf":
        file_type = "pdf"
        content = base64.b64encode(uploaded_file.read()).decode('utf-8')
        content = f"data:application/pdf;base64,{content}"
    elif mime_type == "text/html":
        file_type = "html"
        content = uploaded_file.read().decode('utf-8')
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_type = "docx"
        content = base64.b64encode(uploaded_file.read()).decode('utf-8')
        content = f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{content}"
    elif mime_type == "text/markdown":
        file_type = "md"
        content = uploaded_file.read().decode('utf-8')
    else:
        # Default to txt for other types
        file_type = "txt"
        content = uploaded_file.read().decode('utf-8')

    return content, file_type

def main():
    """Main application function."""
    st.title("Content Rating System")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Select a page", ["Single Rating", "Batch Rating"])
    
    if page == "Single Rating":
        st.header("Rate Single Content")
        
        tab1, tab2 = st.tabs(["📝 Manual Entry", "📄 File Upload"])
        
        with tab1:
            with st.form("manual_rating_form"):
                title = st.text_input("Content Title", key="manual_title")
                content = st.text_area("Content", key="manual_content")
                author = st.text_input("Author", key="manual_author")
                url = st.text_input("URL", key="manual_url")
                
                with st.expander("Metadata", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        keywords = st.text_input("Keywords (comma-separated)", key="manual_keywords")
                        category = st.text_input("Category", key="manual_category")
                    
                    with col2:
                        author_score = st.slider("Author Expertise (0-10)", 0.0, 10.0, 5.0, key="manual_author_score")
                        domain_authority = st.slider("Domain Authority (0-100)", 0.0, 100.0, 50.0, key="manual_domain")
                
                submitted = st.form_submit_button("Rate Content")
                
                if submitted:
                    if not title or not content:
                        st.error("Title and content are required!")
                    else:
                        try:
                            data = {
                                "title": title,
                                "content": content,
                                "author": author,
                                "url": url or f"manual://{title.lower().replace(' ', '-')}",
                                "publication_date": datetime.now().isoformat(),
                                "metadata": {
                                    "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                                    "category": category,
                                    "language": "en",
                                    "author_credentials_score": author_score,
                                    "domain_authority": domain_authority
                                }
                            }
                            
                            with st.spinner("Rating content..."):
                                response = requests.post(f"{API_URL}/rate", json=data)
                                response.raise_for_status()
                                rating = response.json()
                                
                                st.success("Content rated successfully!")
                                display_metrics(rating)
                                
                                fig = create_radar_chart(rating['scores'])
                                st.plotly_chart(fig)
                                
                                with st.expander("View Full Results"):
                                    st.json(rating)
                                    
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with tab2:
            st.info("📁 Supported formats: PDF, HTML, DOCX, Markdown, and Text files")
            
            uploaded_file = st.file_uploader(
                "Upload a file to rate",
                type=['pdf', 'html', 'docx', 'md', 'txt'],
                key="single_upload"
            )
            
            if uploaded_file:
                with st.form("file_rating_form"):
                    st.write("### File Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        - **Name**: {uploaded_file.name}
                        - **Type**: {uploaded_file.type}
                        - **Size**: {uploaded_file.size / 1024:.1f} KB
                        """)
                        
                        title = st.text_input("Title", value=uploaded_file.name)
                        author = st.text_input("Author")
                        url = st.text_input("URL")
                    
                    with col2:
                        with st.expander("Additional Metadata", expanded=True):
                            keywords = st.text_input("Keywords (comma-separated)")
                            category = st.text_input("Category")
                            author_score = st.slider("Author Expertise (0-10)", 0.0, 10.0, 5.0)
                            domain_authority = st.slider("Domain Authority (0-100)", 0.0, 100.0, 50.0)
                    
                    submit_file = st.form_submit_button("Process and Rate")
                    
                    if submit_file:
                        try:
                            content, file_type = get_file_content(uploaded_file)
                            
                            data = {
                                "title": title,
                                "content": content,
                                "author": author,
                                "url": url or f"file://{uploaded_file.name}",
                                "publication_date": datetime.now().isoformat(),
                                "file_type": file_type,
                                "metadata": {
                                    "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                                    "category": category,
                                    "language": "en",
                                    "author_credentials_score": author_score,
                                    "domain_authority": domain_authority,
                                    "file_type": file_type
                                }
                            }
                            
                            with st.spinner("Processing and rating content..."):
                                response = requests.post(f"{API_URL}/rate", json=data)
                                response.raise_for_status()
                                rating = response.json()
                                
                                st.success(f"Successfully processed and rated {uploaded_file.name}")
                                display_metrics(rating)
                                
                                fig = create_radar_chart(rating['scores'])
                                st.plotly_chart(fig)
                                
                                with st.expander("View Full Results"):
                                    st.json(rating)
                                    
                        except Exception as e:
                            st.error(f"Error processing file: {str(e)}")
    
    else:  # Batch Rating page
        st.header("Batch Content Rating")
        st.info("📦 Upload multiple files to rate them in batch")
        
        uploaded_files = st.file_uploader(
            "Upload files",
            type=['pdf', 'html', 'docx', 'md', 'txt'],
            accept_multiple_files=True,
            help="Select multiple files to process in batch"
        )
        
        if uploaded_files:
            st.write(f"### {len(uploaded_files)} Files Selected")
            
            # Show file list
            with st.expander("View Files", expanded=True):
                df = pd.DataFrame([
                    {
                        "Name": f.name,
                        "Type": f.type,
                        "Size (KB)": f"{f.size/1024:.1f}"
                    } for f in uploaded_files
                ])
                st.dataframe(df)
            
            if st.button("Process Batch"):
                try:
                    with st.spinner(f"Processing {len(uploaded_files)} files..."):
                        progress = st.progress(0)
                        
                        resources = []
                        for i, file in enumerate(uploaded_files):
                            content, file_type = get_file_content(file)
                            resources.append({
                                "title": file.name,
                                "content": content,
                                "author": "Unknown",
                                "url": f"file://{file.name}",
                                "publication_date": datetime.now().isoformat(),
                                "file_type": file_type,
                                "metadata": {
                                    "keywords": [],
                                    "category": "Unknown",
                                    "language": "en",
                                    "author_credentials_score": 5.0,
                                    "domain_authority": 50.0,
                                    "file_type": file_type
                                }
                            })
                            progress.progress((i + 1) / len(uploaded_files))
                        
                        response = requests.post(
                            f"{API_URL}/rate-batch",
                            json={"resources": resources}
                        )
                        response.raise_for_status()
                        results = response.json()
                        
                        st.success(f"Successfully processed {len(results['results'])} files")
                        
                        # Display results
                        results_df = pd.DataFrame([
                            {
                                'Title': r['title'],
                                'Score': f"{r['final_score']:.2f}/10",
                                'File Type': r.get('metadata', {}).get('file_type', 'Unknown'),
                                'ID': r['resource_id'][:8]
                            } for r in results['results']
                        ])
                        st.dataframe(results_df)
                        
                        # Download results button
                        st.download_button(
                            "Download Results",
                            data=json.dumps(results, indent=2),
                            file_name="batch_results.json",
                            mime="application/json"
                        )
                        
                except Exception as e:
                    st.error(f"Error processing batch: {str(e)}")

if __name__ == "__main__":
    main()
