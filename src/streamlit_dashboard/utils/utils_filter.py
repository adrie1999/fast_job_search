import pandas as pd
import streamlit as st
from typing import Optional

def get_min_max(data: pd.DataFrame, col: str):
    """
    Get min and max values for a specific column.
    
    Args:
        data (pd.DataFrame): The data to analyze.
        col (str): The column name to get min/max values for.
        
    Returns:
        tuple: A tuple containing the minimum and maximum values for the column.
    """
    return data[col].min(), data[col].max()

def normalize_cosine_similarity(data: pd.DataFrame, col: str):
    """
    Normalize cosine similarity values (range -1 to 1 to 0 to 1).
    
    Args:
        data (pd.DataFrame): The data to process.
        col (str): The column name to normalize.
        
    Returns:
        pd.Series: A normalized version of the column.
    """
    return (data[col] + 1) / 2

def apply_normalization(data: pd.DataFrame, similarity_columns: list):
    """
    Apply normalization to all cosine similarity columns.
    
    Args:
        data (pd.DataFrame): The data to process.
        similarity_columns (list): A list of column names to normalize.
        
    Returns:
        pd.DataFrame: The data with normalized similarity columns.
    """
    for col in similarity_columns:
        data[col] = normalize_cosine_similarity(data, col)
    return data

def create_filters(data: pd.DataFrame, similarity_columns: list):
    """
    Generate filters for similarity columns.
    
    Args:
        data (pd.DataFrame): The data to process.
        similarity_columns (list): A list of similarity columns to create filters for.
        
    Returns:
        dict:  a dictionary of min/max values for each column.
    """
    min_max_values = {col: get_min_max(data, col) for col in similarity_columns}
    return min_max_values

def sidebar_filters(similarity_columns: list, min_max_values: dict, page_name: str,sort_by:bool):
    """
    Render the filters and handle user input for the sidebar.
    
    Args:
        similarity_columns (list): A list of similarity columns for filtering.
        min_max_values (dict): A dictionary with min/max values for each column.
        page_name (str): The name of the page to make keys unique across pages.
        sort_by (bool): having the possibility to change the sort by (false if map).
    Returns:
        tuple: A tuple containing:
            - filters (dict): The filtered values for similarity columns.
            - search_title (str): The job title search string.
            - search_company (str): The company name search string.
            - search_location (str): The location search string.
            - sort_by (str): The column to sort by.
    """
    filters = {}
    with st.sidebar:
        st.header(f"🔎 Filters") 
        search_title = st.text_input("Search Job Title", key=f"{page_name}_search_title")
        search_company = st.text_input("Search Company", key=f"{page_name}_search_company")
        search_location = st.text_input("Search Location", key=f"{page_name}_search_location")

        st.subheader("📊 Similarity Filters")
        for col in similarity_columns:
            min_val, max_val = min_max_values[col]
            filters[col] = st.slider(
                col.replace("_", " ").title(), 
                float(min_val), float(max_val), (float(min_val), float(max_val)),
                key=f"{page_name}_slider_{col}"  
            )
        if sort_by:
            sort_by = st.selectbox("Sort by", similarity_columns, index=0, key=f"{page_name}_sort_by")
        else:
            sort_by=None

    return filters, search_title, search_company, search_location, sort_by


def filter_data(data: pd.DataFrame, filters: dict, search_title: str, search_company: str, search_location: str, sort_by: Optional[str]=None):
    """
    Filter and sort the data based on user input.
    
    Args:
        data (pd.DataFrame): The data to filter.
        filters (dict): The filters for similarity columns.
        search_title (str): The job title to filter by.
        search_company (str): The company to filter by.
        search_location (str): The location to filter by.
        sort_by Optional[(str)]: The column to sort by.
        
    Returns:
        pd.DataFrame: The filtered and sorted data.
    """
    filtered_data = data.copy()
    for col, (min_val, max_val) in filters.items():
        filtered_data = filtered_data[filtered_data[col].between(min_val, max_val)]

    if search_title:
        filtered_data = filtered_data[filtered_data["job_title"].str.contains(search_title, case=False, na=False)]
    if search_company:
        filtered_data = filtered_data[filtered_data["company_name"].str.contains(search_company, case=False, na=False)]
    if search_location:
        filtered_data = filtered_data[filtered_data["job_location"].str.contains(search_location, case=False, na=False)]
    if sort_by is not None:
        filtered_data = filtered_data.sort_values(by=sort_by, ascending=False)
    return filtered_data
