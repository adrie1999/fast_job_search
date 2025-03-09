import streamlit as st
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True, help='Path to your data file')
    return parser.parse_args()

def main():
    args = get_args()
    if 'data_path' not in st.session_state:
        st.session_state.data_path = args.data  

    st.title("🔍 Job Match Exploration Dashboard")

    st.write("### Introduction")
    st.write("""
        This dashboard allows you to explore job matches based on various similarity metrics such as:
        - **Overall match:** cosine similarity between job descriptions and your CV
        - **Skills match:** comparison of job-required skills with your listed skills
        - **Language match:** matching job description language and requirements with your spoken languages
        - **Location match:** job locations compared to your preferred locations
        - **Experience match:** job descriptions compared to your preferred experience

        You can filter and rank job postings to better suit your profile.
    """)

    st.write("### How It Works")
    st.write("""
    1. **Data Collection**: Job postings are scraped from LinkedIn using a configuration file that specifies filters (e.g., keywords, locations, job types).
    2. **Vectorization & Similarity Matching**: We compute embeddings (with distiluse-base-multilingual-cased-v1) for job descriptions and your CV, then apply cosine similarity to rank job postings.
    3. **Preference-based Ranking**: Jobs are ranked based on a combination of:
    - Overall match
    - Matching skills
    - Preferred job titles
    - Experience level
    - Language requirements
    - Location preferences
    4. **Interactive Filtering**: Use the dashboard to refine search results and focus on the best matches.
    5. **Jobs match page**: See the best ranked job offer in a table view with many filters available.
    6. **Jobs locations page**: Explore job locations on a map with multiple filtering options.
    """)

    st.write("### Example of text used for each Similarity metrics")

    cv_text_example = """
    Junior with 2-3 years of experience, graduated in Data Science and Quantitative Finance. A Data Scientist with expertise in machine learning, statistical modeling, and finance. Skilled in extracting insights, building predictive models, and developing data-driven solutions. Currently exploring MLOps to enhance model deployment, monitoring, and scalability.

    Key techniques leveraged: Using Python, developing Streamlit dashboards, building models for signature and checkbox detection, applying clustering and anomaly detection techniques, and using NLP with BERT for text analysis.

    Performing a literature review, collecting accounting and financial data from various sources, applying target balancing techniques, and training models (XGBoost, Random Forest, SVM, and deep learning) to compare their performance with baseline models.
    """

    preferences_example = {
        "skills": "Pandas, Numpy, Sql, SciPy, XGBoost, TensorFlow, Dask, Plotly, Streamlit, Keras, NLP, OpenCV, OCR, Hugging Face, MLflow, Google Cloud Platform, API, Python, PyTorch, PySpark, AWS (EC2/S3), VBA, Scikit-learn, Git/GitLab",
        "title": "Data Scientist, Machine Learning Engineer",
        "location": "France, Germany, Switzerland, Italy, Belgium, Luxembourg",
        "language": "French, Italian, English",
        "experience": "2-3 years experience, Junior, Graduated, Data Scientist"
    }

    st.write("### CV Text Example")
    st.code(cv_text_example, language=None)

    st.write("### Job Preferences Example")
    st.write(preferences_example)



if __name__ == "__main__":
    main()
