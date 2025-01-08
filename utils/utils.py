from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
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
    
def get_html_from_url(url):
    """
    Fetch HTML content from a given URL using Selenium webdriver.
    """
    driver = get_webdriver()
    try:
        driver.get(url)
        # Wait up to 10 seconds for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return driver.page_source
    except TimeoutException:
        raise Exception("Page load timed out")
    except Exception as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    finally:
        driver.quit()

def extract_author_coi(html_content):
    """
    Given a single HTML string, parse out each author's name
    and their 'Conflicts of Interest' statements from any sections
    labeled with 'Authors' Disclosures of Potential Conflicts of Interest'.
    Skips the first author and their disclosures, which is not real author but a title.

    Returns a list of dictionaries:
    [
      {
        "Author": <string>,
        "Disclosures": [<string>, <string>, ...]
      },
      ...
    ]
    """

    soup = BeautifulSoup(html_content, "html.parser")

    # Find all headings that match "Authors' Disclosures..."
    # We look through all heading tags (h1–h6).
    disclosure_headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if "Authors' Disclosures of Potential Conflicts of Interest" in tag.get_text():
            disclosure_headings.append(tag)

    # Helper: check if a tag is any heading
    def is_heading(tag):
        return tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]
    
    all_disclosures = []

    # Parse each COI block separately
    for i, heading in enumerate(disclosure_headings):
        # The block ends at the next "Authors' Disclosures..." heading or EOF
        block_end = disclosure_headings[i+1] if (i+1 < len(disclosure_headings)) else None

        # Gather all siblings between this heading and block_end
        content_tags = []
        nxt = heading.next_sibling
        while nxt and nxt != block_end:
            content_tags.append(nxt)
            nxt = nxt.next_sibling

        # Create a temporary soup of just this block
        block_soup = BeautifulSoup("".join(str(t) for t in content_tags), "html.parser")

        # Find sub-headings that appear to be author names
        # (excludes the heading that might re-mention "Authors' Disclosures...")
        author_headings = []
        for htag in block_soup.find_all(is_heading):
            if "Authors' Disclosures of Potential Conflicts of Interest" not in htag.get_text():
                author_headings.append(htag)

        # For each author heading, gather the paragraphs/divs until the next author heading
        for j, author_tag in enumerate(author_headings):
            # Skip the first author (j == 0)
            if j == 0:
                continue
            
            author_name = author_tag.get_text(strip=True)

            # The next heading (author) is our boundary
            next_heading = author_headings[j+1] if (j+1 < len(author_headings)) else None

            disclosures = []
            sibling = author_tag.next_sibling
            while sibling and sibling != next_heading:
                # If it's a div/p (or similar) that contains text, capture it
                if sibling.name in ["div", "p"]:
                    text_content = sibling.get_text(" ", strip=True)
                    if text_content:
                        disclosures.append(text_content)
                sibling = sibling.next_sibling

            # Store the data
            all_disclosures.append({
                "Author": author_name,
                "Disclosures": disclosures
            })

    return all_disclosures