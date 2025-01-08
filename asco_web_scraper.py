import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup

def get_webdriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome setup failed: {str(e)}")
        raise Exception("Failed to initialize Chrome webdriver")

def extract_author_coi(driver, wait):
    """Extract author conflicts of interest from the disclosures section"""
    try:
        # Find section with author disclosures heading
        disclosure_sections = driver.find_elements(By.TAG_NAME, "section")
        disclosure_section = None
        
        for section in disclosure_sections:
            try:
                heading = section.find_element(By.XPATH, ".//*[self::h2 or self::h3]")
                if "Authors' Disclosures of Potential Conflicts of Interest" in heading.text:
                    disclosure_section = section
                    break
            except NoSuchElementException:
                continue
                
        if not disclosure_section:
            return {}
            
        # Extract individual author disclosures
        author_cois = {}
        current_author = None
        
        # Find all subsections (each author should be in their own subsection)
        subsections = disclosure_section.find_elements(By.TAG_NAME, "section")
        
        for subsection in subsections:
            try:
                # Get author name from h3
                author_heading = subsection.find_element(By.TAG_NAME, "h3")
                if author_heading:
                    current_author = author_heading.text.strip()
                    author_cois[current_author] = {}
                    
                    # Get all paragraphs in this subsection
                    paragraphs = subsection.find_elements(By.TAG_NAME, "p")
                    for p in paragraphs:
                        text = p.text.strip()
                        if ":" in text:
                            # Split on first colon
                            category, details = text.split(":", 1)
                            # Remove bold tags if present
                            category = category.replace("Stock and Other Ownership Interests", "Stock")\
                                            .strip()
                            author_cois[current_author][category] = details.strip()
                            
            except NoSuchElementException:
                continue
                
        return author_cois

    except Exception as e:
        print(f"Error extracting author disclosures: {str(e)}")
        return {}

def extract_countries(driver, wait):
    countries = list() 
    try:
        # Wait for the core-authors section to be present
        authors_section = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "core-authors"))
        )
        
        # More specific CSS selector based on the HTML structure
        affiliations = authors_section.find_elements(
            By.CSS_SELECTOR, 
            'div.affiliations div[property="affiliation"][typeof="Organization"] span[property="name"]'
        )
        
        for affiliation in affiliations:
            try:
                # Get the text using JavaScript to ensure content is loaded
                text = driver.execute_script("return arguments[0].textContent;", affiliation)
                
                if text and "," in text:
                    # Split by comma and get the last part
                    parts = [part.strip() for part in text.split(",")]
                    country = parts[-1]  # Get the last part after comma
                    if country:
                        countries.append(country)
            except Exception as e:
                continue
        return list(countries)
    except Exception as e:
        return []

def scrape_asco_article(url):
    driver = get_webdriver()
    
    try:
        print("Navigating to URL...")
        driver.get(url)
        
        # Add an explicit wait with timeout
        wait = WebDriverWait(driver, 30) 
        print("Page loaded, waiting for elements...")
        
        try:
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[name="dc.Title"]'))
            )
            title = title_element.get_attribute("content")

            author_elements = driver.find_elements(By.CSS_SELECTOR, 'meta[name="dc.Creator"]')
            author_names = [author.get_attribute("content") for author in author_elements]
            
            doi_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[name="dc.Identifier"]'))
            )
            doi = doi_element.get_attribute("content")

            # Extract the abstract
            try:
                abstract_section = wait.until(
                    EC.presence_of_element_located((By.ID, "abstract"))
                )
                # Get all subsections (Purpose, Methods, Results, Conclusion)
                abstract_parts = abstract_section.find_elements(By.TAG_NAME, "section")
                abstract_text = []
                
                for part in abstract_parts:
                    # Get the section title (h3)
                    try:
                        section_title = part.find_element(By.TAG_NAME, "h3").text
                        # Get the section content (div with role="paragraph")
                        content = part.find_element(By.CSS_SELECTOR, 'div[role="paragraph"]').text
                        abstract_text.append(f"{section_title}: {content}")
                    except NoSuchElementException:
                        continue
                
                abstract = "\n\n".join(abstract_text)

            except (TimeoutException, NoSuchElementException):
                abstract = "Abstract not found"
            
            # Extract the publication date
            try:
                pub_date_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[name="dc.Date"]'))
                )
                pub_date = pub_date_element.get_attribute("content")

            except (TimeoutException, NoSuchElementException):
                pub_date = "Publication date not found"
            
            # Extract authors' disclosures
            print("Looking for disclosures...")
            try:
                disclosures_section = wait.until(
                    EC.presence_of_element_located((By.ID, "sec-7")) # always in section 7
                )
                author_cois = extract_author_coi(driver, wait)
            except (TimeoutException, NoSuchElementException):
                author_cois = {}
            
            # Extract countries
            countries = extract_countries(driver, wait)
            
            # Return the extracted information
            return {
                "title": title,
                "authors": author_names,
                "abstract": abstract,
                "publication_date": pub_date,
                "doi": doi,
                "author_disclosures": author_cois,
                "countries": countries
            }
        
        except TimeoutException as te:
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    with open('data/jco_urls.jsonl', 'r') as file:
        urls = [json.loads(line)['url'] for line in file][199:400]
    
    # CSV headers
    headers = ['title', 'authors', 'countries', 'abstract', 'publication_date', 'doi', 'author_disclosures']
    
    # Create/open CSV file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"data/asco_articles_{timestamp}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for url in urls:
            result = scrape_asco_article(url)
            
            if result:
                row = {
                    'title': result['title'],
                    'authors': '; '.join(result['authors']),
                    'countries': '; '.join(result['countries']),
                    'abstract': result['abstract'],
                    'publication_date': result['publication_date'],
                    'doi': result['doi'],
                    'author_disclosures': str(result['author_disclosures'])  # Convert dict to string
                }
                
                writer.writerow(row)
            else:
                print(f"Failed to extract data from: {url}")
            
    
    print("\nAll articles have been processed and saved to asco_articles.csv")
