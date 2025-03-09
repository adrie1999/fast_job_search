import pandas as pd
import numpy as np
import streamlit as st

def add_noise_to_coordinates(data: pd.DataFrame, noise_range: float = 0.0005) -> pd.DataFrame:
    """
    Add random noise to latitude and longitude coordinates in the dataset.

    Args:
        data (pd.DataFrame): The input DataFrame containing 'latitude' and 'longitude' columns.
        noise_range (float, optional): The range of uniform noise to add. Default is 0.0005.

    Returns:
        pd.DataFrame: The DataFrame with modified latitude and longitude values.
    """
    data["latitude"] += np.random.uniform(-noise_range, noise_range, size=len(data))
    data["longitude"] += np.random.uniform(-noise_range, noise_range, size=len(data))
    return data

@st.cache_data
def load_data(data_path) -> pd.DataFrame:
    """
    Load job data from a Parquet file and add noise to latitude and longitude.
    This function ensures the data is only loaded and processed once.

    Returns:
        pd.DataFrame: The loaded and modified DataFrame.
    """
    data = pd.read_parquet(data_path)
    data_with_noise = add_noise_to_coordinates(data)
    
    return data_with_noise

def get_data(data_path) -> pd.DataFrame:
    """
    Retrieve the job data, loading it into session state if not already cached.

    Returns:
        pd.DataFrame: The job data stored in session state.
    """
    if "data" not in st.session_state:
        st.session_state.data = load_data(data_path)
    return st.session_state.data
