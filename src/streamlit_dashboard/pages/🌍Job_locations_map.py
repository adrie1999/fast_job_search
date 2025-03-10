import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from utils.data_loader import get_data
from utils.utils_filter import (
    apply_normalization,
    create_filters,
    sidebar_filters,
    filter_data,
)

data_path = "Data/streamlit_data/data_streamlit.parquet"
data = get_data(data_path).copy()


similarity_columns = [
    "overall_similarity",
    "skills_similarity",
    "title_similarity",
    "location_similarity",
    "language_similarity",
    "experience_similarity",
]

data = apply_normalization(data, similarity_columns)

min_max_values = create_filters(data, similarity_columns)

filters, search_title, search_company, search_location, sort_by = sidebar_filters(
    similarity_columns, min_max_values, page_name="job_location", sort_by=False
)

filtered_data = filter_data(
    data.copy(), filters, search_title, search_company, search_location, sort_by
)

st.markdown("### 🌍 Job locations map")
st.markdown(f"### Showing {len(filtered_data)} jobs")

m = folium.Map(location=[50.0, 20.0], zoom_start=4)
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_data.iterrows():
    if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])

            if pd.notna(row["job_url"]):
                popup_html = (
                    f'<a href="{row["job_url"]}" target="_blank">{row["job_title"]}</a>'
                )
            else:
                popup_html = row["job_title"]

            popup = folium.Popup(popup_html, max_width=300)
            folium.Marker([lat, lon], popup=popup).add_to(marker_cluster)

        except ValueError:
            continue

st_folium(m, width=1200, height=600)
