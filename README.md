# 📌 Fast Job Search

Fast Job Search is a job-matching system that scrapes job postings from LinkedIn, applies NLP-based similarity matching with user CVs, and presents ranked job opportunities in a Streamlit dashboard.

### 📊 Dashboard Demo  

My streamlit dashboard demo is available [here](https://adrie1999-fast-job-search-srcstreamlit-dashboardapp-x6lxah.streamlit.app/).  

### 🚀 Features

Web Scraping: Extract job postings from LinkedIn using Selenium.

NLP Matching: Compare job descriptions with a candidate's CV using embedding of `distiluse-base-multilingual-cased-v1` and cosine similarity.

Ranking System: Sort job postings based on relevance (skills, title, location, language, experience).

Streamlit Dashboard: Visualize job matches with interactive filtering, including a job location map.

Job Data Storage: Save scrapped job data as Parquet files and manage them efficiently.

### 📁 Project Structure
```
fast_job_search/
│️── Data/
│️   ├── save_jobs_data/         # Raw job postings stored as Parquet files
│️   ├── streamlit_data/         # Processed data for Streamlit visualization
│️── src/
│️   ├── utils                   # utils methods for main script
│️   ├── Web_scrapping/           # LinkedIn web scraper
│️   ├── job_match/          # NLP-based job matching
│️   ├── streamlit_dashboard/    # Streamlit app for job exploration
│️── .gitignore                  # Files and folders ignored by Git
│️── requirements.txt            # Python dependencies
│️── README.md                   # Project documentation
```
### 🛠️ Installation

1️⃣ Clone the Repository

```
git clone git@github.com:adrie1999/fast_job_search.git
cd fast_job_search
```

2️⃣ Set Up a Virtual Environment

```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

4️⃣ Set Up Git LFS (For Large Parquet Files)

```
git lfs install
git lfs track "*.parquet"
git add .gitattributes
git commit -m "Track Parquet files with Git LFS"
git push origin main
```

### 🚀 Usage

Run the Web Scraper and mathing job algorithm

```
python src/main.py
```


Run the Streamlit Dashboard

```
streamlit run src/streamlit_dashboard/app.py
```

### ⚠️ Warning
Do not use this code to spam LinkedIn with a lot of requests in a short period. Your account could be banned.

### 👤 Author

Adrien CHAILLOUT-MORLOT - Data Scientist & GitHub: adrie1999
