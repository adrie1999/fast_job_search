import streamlit as st
import pandas as pd
from utils.data_loader import get_data
from utils.utils_filter import apply_normalization,create_filters,sidebar_filters,filter_data


data = get_data(st.session_state.data_path).copy()

similarity_columns = [
    "overall_similarity", "skills_similarity", "title_similarity", 
    "location_similarity", "language_similarity", "experience_similarity"
]

data = apply_normalization(data, similarity_columns)

min_max_values = create_filters(data, similarity_columns)

filters, search_title, search_company, search_location, sort_by = sidebar_filters(similarity_columns, min_max_values, page_name='job_match',sort_by=True)

filtered_data = filter_data(data.copy(), filters, search_title, search_company, search_location, sort_by)


def make_clickable(title, url):
    if pd.notna(url):
        return f'<a href="{url}" target="_blank">{title}</a>'
    return title

filtered_data["job_title"] = filtered_data.apply(lambda row: make_clickable(row["job_title"], row["job_url"]), axis=1)

column_rename_map = {
    "job_title": "Job Title",
    "company_name": "Company",
    "job_location": "Location",
    "overall_similarity": "Overall Match",
    "skills_similarity": "Skills Match",
    "title_similarity": "Title Match",
    "location_similarity": "Location Match",
    "language_similarity": "Language Match",
    "experience_similarity": "Experience Match",
}

display_data = filtered_data.rename(columns=column_rename_map)
st.markdown("### 🔍 Explore and rank job matches based on your profile")
st.markdown(f"### Showing {len(display_data)} jobs")
st.write(display_data[list(column_rename_map.values())].to_html(escape=False, index=False), unsafe_allow_html=True)
