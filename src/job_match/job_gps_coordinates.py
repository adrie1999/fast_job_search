from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas as pd
from typing import Optional, Tuple
import re


class GpsFinder:
    def __init__(self, data_jobs: pd.DataFrame):
        """
        Initialize the GpsFinder class with the path to job data.

        Args:
            job dataframe (pd.DataFrame): Job dataframe after job matching.
        """
        self.data_jobs = data_jobs

    def remove_job_type_data(self) -> pd.DataFrame:
        """
        And remove text like (remote working) etc..

        Returns:
            pd.DataFrame: A pandas DataFrame containing job data.
        """
        self.data_jobs["job_location"] = self.data_jobs["job_location"].apply(
            self._remove_text_in_parentheses
        )

    def _remove_text_in_parentheses(self, text: str) -> str:
        """
        Remove all text inside parentheses (including the parentheses) from a given string.

        Args:
            text (str): The input string from which text inside parentheses needs to be removed.

        Returns:
            str: The modified string with text inside parentheses removed.
        """
        return re.sub(r"\s?\(.*?\)", "", text)

    def get_gps_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get GPS coordinates (latitude, longitude) from a location string.

        Args:
            location (str): The location as a text string (e.g., "Amsterdam, Hollande Septentrionale, Pays-Bas").

        Returns:
            Optional[Tuple[float, float]]: A tuple with (latitude, longitude) if found, else None.
        """
        geolocator = Nominatim(user_agent="geo_locator")

        try:
            location_data = geolocator.geocode(location, timeout=30)
            if location_data:
                return location_data.latitude, location_data.longitude
        except GeocoderTimedOut:
            print("Geocoding request timed out. Try again.")
        return None

    def process_job_locations(self) -> pd.DataFrame:
        """
        Process job locations and add GPS coordinates to the job data.

        Returns:
            pd.DataFrame: DataFrame with added latitude and longitude columns.
        """
        self.remove_job_type_data()
        self.data_jobs["coordinates"] = self.data_jobs["job_location"].apply(
            self.get_gps_coordinates
        )
        self.data_jobs[["latitude", "longitude"]] = pd.DataFrame(
            self.data_jobs["coordinates"].tolist(), index=self.data_jobs.index
        )
        self.data_jobs.drop(columns=["coordinates"], inplace=True)
        return self.data_jobs

    def get_job_with_coordinates(self) -> pd.DataFrame:
        """
        Get the job data with latitude and longitude information for each job.

        Returns:
            pd.DataFrame: DataFrame containing job information with latitude and longitude columns.
        """
        return self.process_job_locations()
