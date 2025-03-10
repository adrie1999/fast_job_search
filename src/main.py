from job_match.job_match import similarity_jobs_vs_cv
from job_match.job_gps_coordinates import GpsFinder
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from web_scrapping.web_scrap_lk import LinkedingJobScrapper
from utils.utils import get_most_recent_file
import os
import logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set up logging configuration with relative paths
log_dir = os.path.join(base_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO, can be adjusted to DEBUG or ERROR
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(
            os.path.join(log_dir, "scraping_process.log")
        ),  # Log to a file in 'logs' folder
    ],
)

if __name__ == "__main__":
    # Relative paths based on the current script's directory
    path_chrome_profil = "user-data-dir=/home/adrien/.config/google-chrome/"
    path_save_scrapping_parquet = os.path.join(base_dir, "Data/save_jobs_data")
    path_config_scrapping = os.path.join(
        base_dir, "src/web_scrapping", "config_scrapping.yaml"
    )
    path_data_save_streamlit = os.path.join(base_dir, "Data", "streamlit_data")

    logging.info("Starting the web scraping process")
    # chromedriver conf
    options = Options()
    options.add_argument(path_chrome_profil)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--headless")

    logging.info("Initializing the Chrome WebDriver")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    # web scrapping and saving data

    logging.info("Initializing the LinkedIn Job Scraper")
    web_scrapper = LinkedingJobScrapper(driver, config_path=path_config_scrapping)

    logging.info("Running the web scraper to collect job listings")
    job_listings_full = web_scrapper.run()

    logging.info("Saving scraped job listings to Parquet")
    web_scrapper.save_listing_to_parquet(
        job_listings_full, saving_path=path_save_scrapping_parquet
    )

    logging.info("Fetching the most recent scraped data file")
    path_scrapped_parquet = get_most_recent_file(path_save_scrapping_parquet)

    logging.info("Running similarity search on job listings")
    # Vector search based on text and preferences
    cv_text_example = """
    Junior with 2-3 years of experience Graduated in Data science and Quantative Finance. Data Scientist with expertise in machine learning, statistical modeling, and finance. Skilled in extracting insights, building predictive models, and developing data-driven solutions. Currently exploring MLOps to enhance model deployment, monitoring, and scalability.

    Key leveraged techniques: Using python, developing Streamlit dashboards, building models for signature and checkbox detection, applying clustering and anomaly detection techniques, and using NLP with BERT for text analysis

    Performing a literature review, collecting accounting and financial data from various sources, applying target balancing techniques, and training models (XGBoost, Random Forest, SVM, and deep learning) to compare their performance with the baseline model
    """
    preferences_example = {
        "skills": "Pandas, Numpy, Sql, SciPy, Xgboost, Tensorflow, Dask, Plotly, Streamlit, Keras, NLP,OpenCV, OCR, Hugging Face, MLflow, Google Could Platform, API,Python,Pytorch,PySpark, AWS (EC2/S3) ,VBA, Scikit-learn,Git/Gitlab",
        "title": "Data Scientist, Machine Learning Engineer",
        "location": "France, Germany, Switzerland, Italy, Belgium, Luxembourg",
        "language": "French, Italian, English",
        "experience": "2-3 years experience, Junior, Graduated, Data scientist",
    }
    ranked_jobs = similarity_jobs_vs_cv(
        path_scrapped_parquet, cv_text_example, preferences_example, top_n=1000
    )

    logging.info("Fetching job coordinates for visualization")
    # Get job gps coordinates for ploting purpose in streamlit
    ranked_jobs = GpsFinder(ranked_jobs).get_job_with_coordinates()

    logging.info(f"Saving final data to {path_data_save_streamlit}")
    # Save final streamlit  data
    if not os.path.exists(path_data_save_streamlit):
        os.makedirs(path_data_save_streamlit)
    ranked_jobs.to_parquet(
        os.path.join(path_data_save_streamlit, "data_streamlit.parquet")
    )

    logging.info("Web scraping and data processing completed successfully")
