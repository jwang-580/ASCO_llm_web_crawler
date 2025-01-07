# scraping asco website https://ascopubs.org/doi/10.1200/JCO.23.00975

import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_webdriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # Add user agent to avoid detection
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome setup failed: {str(e)}")
        raise Exception("Failed to initialize Chrome webdriver")

def extract_author_coi(disclosures_section):
    """Helper function to extract individual author COIs"""
    author_cois = {}
    
    # Find all sections with data-type="coi-statement"
    coi_sections = disclosures_section.find_elements(By.CSS_SELECTOR, 'section[data-type="coi-statement"]')
    
    for section in coi_sections:
        try:
            # Get author name (h4)
            author_name = section.find_element(By.TAG_NAME, "h4").text
            
            # Get all disclosure paragraphs
            disclosure_paragraphs = section.find_elements(By.CSS_SELECTOR, 'div[role="paragraph"]')
            disclosures = []
            
            for para in disclosure_paragraphs:
                text = para.text
                if text and not text.startswith("No other potential conflicts"):  # Skip the final note
                    disclosures.append(text)
            
            if disclosures:
                author_cois[author_name] = disclosures
            else:
                author_cois[author_name] = ["No conflicts reported"]
                
        except NoSuchElementException:
            continue
    
    return author_cois

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
            
            # Extract authors' disclosures (if available)
            print("Looking for disclosures...")
            try:
                disclosures_section = wait.until(
                    EC.presence_of_element_located((By.ID, "sec-7"))
                )
                # Extract individual author COIs
                author_cois = extract_author_coi(disclosures_section)
                print(f"Found disclosures for {len(author_cois)} authors")
            except (TimeoutException, NoSuchElementException):
                print("Disclosures section not found")
                author_cois = {}
            
            # Return the extracted information
            return {
                "title": title,
                "authors": author_names,
                "abstract": abstract,
                "publication_date": pub_date,
                "author_disclosures": author_cois
            }
        
        except TimeoutException as te:
            print(f"Timeout while waiting for element: {str(te)}")
            # Take screenshot for debugging
            driver.save_screenshot("error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Take screenshot for debugging
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        except:
            print("Could not save error screenshot")
        return None
        
    finally:
        driver.quit()

# Usage
if __name__ == "__main__":
    #url = "https://ascopubs.org/doi/10.1200/JCO.23.00975"
    url = "https://ascopubs.org/doi/10.1200/JCO.21.01963"
    result = scrape_asco_article(url)
    
    if result:
        print("\nExtracted Data:")
        print("-" * 50)
        print("Title:", result["title"])
        print("\nAuthors:", ", ".join(result["authors"]))
        print("\nAbstract:", result["abstract"])
        print("\nPublication Date:", result["publication_date"])
        print("\nAuthor Disclosures:")
        for author, cois in result["author_disclosures"].items():
            print(f"\n{author}:")
            for coi in cois:
                print(f"  - {coi}")
    else:
        print("Failed to extract data from the article")
