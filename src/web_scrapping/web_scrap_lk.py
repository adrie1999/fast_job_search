import yaml
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
import os
import pandas as pd
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
import random

class LinkedingJobScrapper:
    def __init__(self,driver: WebDriver,config_path: str = "config.yaml", timeout: int = 4)-> None:
        if not isinstance(driver, webdriver.Chrome):
            raise TypeError("Expected driver to be an instance of webdriver.Chrome")
        self.driver=driver
        self.config_path=config_path
        self.timeout= timeout

    def load_config(self) -> Optional[Dict]:
        """
        Loads the YAML configuration file.

        Returns:
        - dict: Parsed configuration data, or None if loading fails.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            return config.get("config")
        except FileNotFoundError:
            print("Error: Configuration file not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
        return None

    def search_url(self,url) -> None:
        """
        Navigates to the given URL and waits for the page to load.

        Args:
        - url (str): The target URL to visit.
        """
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print(f"Successfully loaded URL: {url}")

        except Exception as e:
            print(f"Error loading URL {url}: {e}")



    def login_linkendin(self,linkedin_email: str, linkedin_password: str) -> None:
        """
        Logs into LinkedIn and searches for jobs using the given URL.

        Args:
        - linkedin_email (str): LinkedIn login email.
        - linkedin_password (str): LinkedIn login password.
        - url (str): LinkedIn job search URL.
        """
        try:
            button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="base-contextual-sign-in-modal"]/div/section/div/div/div/div[2]/button'))
            )
            self.driver.execute_script("arguments[0].click();", button)
            print("button sign in clicked successfully.")
        except Exception as e:
            print(f"Error clicking second button: {e}")
            return

        try:
            email_field = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "base-sign-in-modal_session_key"))
            )
            password_field = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "base-sign-in-modal_session_password"))
            )
            email_field.send_keys(linkedin_email)
            password_field.send_keys(linkedin_password)
            print("Credentials entered successfully.")
        except Exception as e:
            print(f"Error entering credentials: {e}")
            return

        try:
            sign_in_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="base-sign-in-modal"]/div/section/div/div/form/div[2]/button'))
            )
            self.driver.execute_script("arguments[0].click();", sign_in_button)
            print("Login successful.")
        except Exception as e:
            print(f"Error clicking login button: {e}")
            return  
        
    def generate_linkedin_job_url(self,job_title: str, location: str, time_range: str = 'r86400') -> str:
        """
        Generates a LinkedIn job search URL.

        Args:
        - job_title (str): The job title to search for.
        - location (str): The location (country/city) to filter jobs.
        - time_range (str): Time range for job postings (default is last 2self.timeout hours).

        Returns:
        - str: LinkedIn job search URL.
        """
        base_url = 'https://www.linkedin.com/jobs/search/'
        job_title_encoded = job_title.replace(' ', '%20')
        location_encoded = location.replace(' ', '%20')
        
        return f'{base_url}?f_TPR={time_range}&keywords={job_title_encoded}&location={location_encoded}&origin=JOB_SEARCH_PAGE_JOB_FILTER'

    def scroll_job_cards(self,num_scrolls: int = 5) -> None:
        """
        Scrolls through job card elements inside the job search list.

        Args:
        - num_scrolls (int): Number of scroll iterations (default is 1).
        """
        for i in range(num_scrolls):
            try:
                job_cards = self.driver.find_elements(By.XPATH, '//li[contains(@class, "occludable-update")]')
                n_item=len(job_cards)
                if job_cards:
                    if i==num_scrolls-1:
                        index=-1
                    else:
                        index=int(n_item/(num_scrolls-i))
                    time.sleep(random.uniform(0.5, 2))
                    self.driver.execute_script("arguments[0].scrollIntoView();", job_cards[index])
            except Exception as e:
                print(f"Scrolling error: {e}")
                break
        print("Scrolling completed.")

    def click_next_page(self) -> None:
        """
        Clicks the 'Next Page' button in LinkedIn job search and waits for the page to load.

        """
        try:
            time.sleep(random.uniform(0.5, 2))
            current_page = self.driver.find_element(By.XPATH, '//li[contains(@class, "selected")]/button')
            current_page_number = int(current_page.text.strip())

            next_page_xpath = f'//li[@data-test-pagination-page-btn="{current_page_number + 1}"]/button'
            next_page_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, next_page_xpath))
            )

            next_page_button.click()
            print(f"Navigated to page {current_page_number + 1}")

            WebDriverWait(self.driver, self.timeout).until(
                EC.staleness_of(next_page_button) 
            )
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "occludable-update")]'))
            )

        except Exception as e:
            print(f"Error clicking next page: {e}")



    def get_max_page_number(self) -> int:
        """
        Retrieves the maximum number of pages available in the LinkedIn job search results.

        Returns:
        - int: The highest page number available.
        """
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "artdeco-pagination__indicator")]'))
            )

            pagination_buttons = self.driver.find_elements(By.XPATH, '//li[@data-test-pagination-page-btn]/button')

            page_numbers = [int(btn.get_attribute("aria-label").replace("Page ", "")) for btn in pagination_buttons]
            max_page = max(page_numbers) if page_numbers else 1

            print(f"Maximum number of pages: {max_page}")
            return max_page

        except Exception as e:
            print(f"Error retrieving max page number: {e}")
            return 1 


    def scrape_all_job_listings_with_selenium(self) -> List[Dict[str, Optional[str]]]:
        """
        Scrapes job listings from LinkedIn job search results.

        Returns:
        - List[Dict]: List of job details dictionaries.
        """
        job_listings = []
        
        try:
            job_cards = self.driver.find_element(By.CLASS_NAME,"hGByQEOVDCYtBdgZhMutwkWZGDYyuVk").find_elements(By.CLASS_NAME, "job-card-container")
            for i, job_card in enumerate(job_cards):
                if i > 0:
                    ActionChains(self.driver).move_to_element(job_card).perform()
                    job_card.click()
                    time.sleep(random.uniform(0.5, 2))
                try:
                    job_title_element = job_card.find_element(By.CLASS_NAME, "job-card-container__link")
                    job_title = job_title_element.find_element(By.CLASS_NAME, "visually-hidden").text.strip()
                except:
                    job_title = None

                try:
                    company_name = job_card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text.strip()
                except:
                    company_name = None

                try:
                    job_location = job_card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__caption").text.strip()
                except:
                    job_location = None

                try:
                    job_url = job_card.find_element(By.CLASS_NAME, "job-card-container__link").get_attribute("href")
                except:
                    job_url = None
                try:
                    job_description = self.driver.find_element(By.CLASS_NAME,"jobs-description__container").find_element(By.CLASS_NAME, "mt4").text
                    job_description=job_description.replace("\n", " ")
                    
                except:
                    job_description = None

                job_data = {
                    "job_title": job_title,
                    "company_name": company_name,
                    "job_location": job_location,
                    "job_url": job_url,
                    "job_description": job_description
                }

                job_listings.append(job_data)
            
            print(f"Scraped {len(job_listings)} job listings.")
        except Exception as e:
            print(f"Scraping error: {e}")

        return job_listings


    def run(self) -> None:
        job_listings_full=[]
        config = self.load_config()
        if not config:
            return
        
        for search_i,location in enumerate(config['job_search']['locations']):
            url = self.generate_linkedin_job_url(config['job_search']['keyword'], location)
            self.search_url(url)
            if search_i==0:
                self.login_linkendin(config['linkedin_email'], config['linkedin_password'])
            max_page=self.get_max_page_number()
            for i in range(min(config['job_search']['num_pages'],max_page)):
                self.scroll_job_cards(num_scrolls=10)
                job_listings=self.scrape_all_job_listings_with_selenium()  
                if i<min(config['job_search']['num_pages'],max_page)-1:
                    self.click_next_page()
                job_listings_full.extend(job_listings)
        return job_listings_full


    def save_listing_to_parquet(self, job_listings_full: List[Dict[str, str]], saving_path: str ) -> None:
        """
        Saves job listings to a Parquet file, organizing by the current hour.

        Args:
        - job_listings_full (List[Dict[str, str]]): List of job listings where each listing is a dictionary with job details.
        - saving_path (str): Directory where the Parquet file will be saved.
        """
        df = pd.DataFrame(job_listings_full)
        current_datetime = datetime.now()
        formatted_date_hour = current_datetime.strftime("%Y-%m-%d_%H") 
        directory = os.path.join(saving_path, f'parquet_files/{formatted_date_hour}')
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"data_{formatted_date_hour}.parquet")

        df.to_parquet(file_path, engine='pyarrow')

        print(f"Parquet file saved successfully at: {file_path}")








