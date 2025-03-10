import pandas as pd
import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from job_match.utils import get_language_name


class JobsMatcherCV:
    def __init__(
        self,
        path_data: str,
        model_name: str = "sentence-transformers/distiluse-base-multilingual-cased-v1",
    ):
        """
        Initializes the job matcher with a dataset and an NLP model.

        Args:
        - path_data (str): Path to the job listings dataset (Parquet file).
        - model_name (str): Name of the SentenceTransformer model (default: all-MiniLM-L6-v2).
        """
        self.path_data = path_data
        self.model = SentenceTransformer(model_name)

    @property
    @lru_cache(maxsize=1)
    def data(self) -> pd.DataFrame:
        """
        Loads the job listings data from a Parquet file and removes duplicates.

        Returns:
        - pd.DataFrame: DataFrame containing unique job listings.
        """
        try:
            df = pd.read_parquet(self.path_data)
            df = df.drop_duplicates(
                subset=["job_title", "company_name", "job_description"]
            )
            df["job_title"] = df["job_title"].str.replace(
                r"\swith verification", "", regex=True
            )
            return df
        except Exception as e:
            raise ValueError(f"Error loading job data: {e}")

    def get_job_descriptions(self) -> List[str]:
        """
        Retrieves the job descriptions by combining job title and job description.

        Returns:
        - List[str]: List of jobs descriptions.
        """
        return (self.data["job_title"] + " " + self.data["job_description"]).tolist()

    def get_job_locations(self) -> List[str]:
        """
        Retrieves the jobs locations.

        Returns:
        - List[str]: List of job location.
        """
        return (self.data["job_location"]).tolist()

    def get_job_title(self) -> List[str]:
        """
        Retrieves the job title.

        Returns:
        - List[str]: List of job location.
        """
        return (self.data["job_title"]).tolist()

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generates sentence embeddings for a list of texts.

        Args:
        - texts (List[str]): List of text inputs to encode.

        Returns:
        - np.ndarray: Matrix of embeddings.
        """
        return self.model.encode(texts, convert_to_tensor=True)

    def rank_jobs(
        self, cv_text: str, preferences: Dict[str, str], top_n: int = 10
    ) -> pd.DataFrame:
        """
        Ranks job positions based on similarity across different categories.

        Args:
        - cv_text (str): CV content as a string.
        - preferences (Dict[str, str]): Dictionary of user preferences (skills, location, etc.).
        - top_n (int): Number of top-ranked jobs to return.

        Returns:
        - pd.DataFrame: DataFrame with the top-ranked job positions and category-wise scores.
        """
        job_texts = self.get_job_descriptions()
        job_embeddings = self.get_embeddings(job_texts)

        job_language_texts = [
            f"Language of the text : {get_language_name(job_text)}  Job offer: {job_text}"
            for job_text in job_texts
        ]
        job_language_embeddings = self.get_embeddings(job_language_texts)

        job_title_texts = self.get_job_title()
        job_title_embeddings = self.get_embeddings(job_title_texts)

        job_location_texts = self.get_job_locations()
        job_location_embeddings = self.get_embeddings(job_location_texts)

        cv_embedding = self.get_embeddings([cv_text])[0]

        overall_similarity = cosine_similarity(
            [cv_embedding.cpu().numpy()], job_embeddings.cpu().numpy()
        ).flatten()

        category_scores = {}

        for category, preference_text in preferences.items():
            if category == "title":
                preference_embedding = self.get_embeddings([preference_text])[0]
                category_similarity = cosine_similarity(
                    [preference_embedding.cpu().numpy()],
                    job_title_embeddings.cpu().numpy(),
                ).flatten()
            elif category == "location":
                preference_embedding = self.get_embeddings([preference_text])[0]
                category_similarity = cosine_similarity(
                    [preference_embedding.cpu().numpy()],
                    job_location_embeddings.cpu().numpy(),
                ).flatten()
            if category == "title":
                preference_embedding = self.get_embeddings([preference_text])[0]
                category_similarity = cosine_similarity(
                    [preference_embedding.cpu().numpy()],
                    job_title_embeddings.cpu().numpy(),
                ).flatten()
            elif category == "language":
                preference_embedding = self.get_embeddings([preference_text])[0]
                category_similarity = cosine_similarity(
                    [preference_embedding.cpu().numpy()],
                    job_language_embeddings.cpu().numpy(),
                ).flatten()
            else:
                preference_embedding = self.get_embeddings([preference_text])[0]
                category_similarity = cosine_similarity(
                    [preference_embedding.cpu().numpy()], job_embeddings.cpu().numpy()
                ).flatten()

            category_scores[category] = category_similarity

        self.data["overall_similarity"] = overall_similarity
        for category, scores in category_scores.items():
            self.data[f"{category}_similarity"] = scores

        ranked_jobs = self.data.sort_values(
            by="overall_similarity", ascending=False
        ).head(top_n)

        return ranked_jobs[
            [
                "job_title",
                "company_name",
                "job_location",
                "job_url",
                "job_description",
                "overall_similarity",
            ]
            + [f"{cat}_similarity" for cat in category_scores.keys()]
        ]


def similarity_jobs_vs_cv(
    path_data: str, cv_text: str, preferences: Dict[str, str], top_n: int = 10
) -> pd.DataFrame:
    """
    Matches the CV against job descriptions and returns ranked job positions.

    Args:
    - path_data (str): Path to job dataset.
    - cv_text (str): CV text as a string.
    - preferences (Dict[str, str]): Dictionary containing user preferences for ranking.
    - top_n (int): Number of top jobs to return.

    Returns:
    - pd.DataFrame: Ranked DataFrame with category-wise similarity scores.
    """
    matcher = JobsMatcherCV(path_data)
    return matcher.rank_jobs(cv_text, preferences, top_n)
