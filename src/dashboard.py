"""
Streamlit Dashboard for IDE Index
Visualize digital transformation initiatives

To run:
    streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager
from config import Config


@st.cache_resource
def load_database():
    """Load database connection"""
    return DatabaseManager(db_path=str(Config.DATABASE_PATH))


@st.cache_data
def load_data(_db):
    """Load all initiatives data"""
    initiatives = _db.get_all_initiatives()
    if not initiatives:
        return pd.DataFrame()
    return pd.DataFrame(initiatives)


def main():
    st.set_page_config(
        page_title="IDE Index Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Header
    st.title("🌐 Islamic Digital Economy (IDE) Index")
    st.markdown("### Digital Transformation Initiatives Dashboard")
    st.markdown("---")
    
    # Load data
    db = load_database()
    df = load_data(db)
    
    if df.empty:
        st.warning("⚠️ No data found in database. Please run the extraction pipeline first.")
        st.code("python src/main.py")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Company filter
    companies = ['All'] + sorted(df['company_name'].unique().tolist())
    selected_company = st.sidebar.selectbox("Company", companies)
    
    # Category filter
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Year filter
    years = ['All'] + sorted(df['year_mentioned'].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Year", years)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['company_name'] == selected_company]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_year != 'All':
        filtered_df = filtered_df[filtered_df['year_mentioned'] == selected_year]
    
    # Statistics
    stats = db.get_statistics()
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", stats['total_companies'])
    with col2:
        st.metric("Total Reports", stats['total_reports'])
    with col3:
        st.metric("Total Initiatives", stats['total_initiatives'])
    with col4:
        st.metric("Filtered Results", len(filtered_df))
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Initiatives by Category")
        category_counts = filtered_df['category'].value_counts()
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Initiatives by Year")
        year_counts = filtered_df['year_mentioned'].value_counts().sort_index()
        fig = px.bar(
            x=year_counts.index,
            y=year_counts.values,
            labels={'x': 'Year', 'y': 'Number of Initiatives'},
            title="Trend Over Years"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Company comparison
    st.subheader("🏢 Company Comparison")
    company_counts = filtered_df['company_name'].value_counts().head(10)
    fig = px.bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        labels={'x': 'Number of Initiatives', 'y': 'Company'},
        title="Top 10 Companies by Initiative Count"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Technology word cloud (simple version)
    st.subheader("💻 Top Technologies Mentioned")
    tech_text = ' '.join(filtered_df['technology_used'].dropna().tolist())
    tech_words = tech_text.split()
    tech_counts = pd.Series(tech_words).value_counts().head(20)
    
    fig = px.bar(
        x=tech_counts.values,
        y=tech_counts.index,
        orientation='h',
        labels={'x': 'Frequency', 'y': 'Technology'},
        title="Most Frequently Mentioned Technologies"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data table
    st.markdown("---")
    st.subheader("📋 Detailed Initiatives")
    
    # Display controls
    col1, col2 = st.columns([3, 1])
    with col2:
        show_all_columns = st.checkbox("Show all columns", False)
    
    if show_all_columns:
        display_df = filtered_df
    else:
        display_df = filtered_df[[
            'company_name', 'category', 'initiative', 
            'technology_used', 'year_mentioned'
        ]]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="ide_initiatives.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Islamic Digital Economy (IDE) Index Dashboard</p>
            <p>Built with Streamlit • Data extracted using OpenAI GPT</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
