from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from bs4 import BeautifulSoup
import re

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
        text = tag.get_text()
        if "Authors' Disclosures of Potential Conflicts of Interest" in text or \
            "Authors’ Disclosures of Potential Conflicts of Interest" in text:
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
        if author_headings:
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

        else:
            # SCENARIO B: No author subheadings. All authors in one or more <div>/<p> blocks with <b> labels.
            text_blocks = block_soup.find_all(["div", "p"])
            for block in text_blocks:
                b_tags = block.find_all("b")
                # For each <b> label like: <b>Employment or Leadership Position:</b> ...
                for btag in b_tags:
                    raw_label = btag.get_text(" ", strip=True)  # e.g. "Employment or Leadership Position:"
                    parent_text = block.get_text(" ", strip=True)

                    # (A) Normalize the label
                    #     1) Drop the word " Position" if present
                    #     2) Ensure we have "Employment or Leadership:" form
                    #     3) Remove trailing colon for easier pattern match
                    label_clean = raw_label.replace(" Position", "")  # remove " Position"
                    label_clean = re.sub(r':$', '', label_clean).strip()  # remove trailing colon
                    # e.g. "Employment or Leadership"

                    # We'll keep it consistent by re-adding a colon for final output
                    label_clean += ":"

                    # (B) Find the text chunk that belongs to this label
                    #    We locate everything after the label, up to the next <b> label
                    #    by scanning the entire block's text.
                    #    We'll form a small pattern for our label, ignoring optional colon/spaces
                    pattern_label = re.escape(raw_label.rstrip(':')) + r':?\s*(.*)'
                    # e.g. "Employment\ or\ Leadership\ Position:?\s*(.*)"

                    m = re.search(pattern_label, parent_text)
                    if not m:
                        continue  # can't find text after the label

                    # We'll get the substring from the match
                    authors_string = m.group(1)

                    # Next label starts?
                    # We'll gather all other <b> labels in this block and see which one starts after this
                    all_labels_in_block = []
                    for other_b in b_tags:
                        other_l = other_b.get_text(" ", strip=True).rstrip(':')
                        for mm in re.finditer(re.escape(other_l), parent_text):
                            all_labels_in_block.append((mm.start(), other_l))
                    all_labels_in_block.sort(key=lambda x: x[0])

                    # Our substring begins at m.start(1)
                    our_start = m.start(1)
                    next_label_index = None
                    for (pos, lbl) in all_labels_in_block:
                        if pos > our_start:
                            next_label_index = pos
                            break

                    if next_label_index:
                        length_to_cut = next_label_index - our_start
                        authors_string = authors_string[:length_to_cut]

                    # (C) Now we have the chunk for this label, e.g.
                    #   "Robert Weaver, Florida Cancer Specialists (C); Elizabeth Crowley, Celldex Therapeutics (C)"
                    # Split on semicolons
                    people_chunks = [p.strip() for p in authors_string.split(';') if p.strip()]

                    for chunk in people_chunks:
                        # chunk e.g. "Robert Weaver, Florida Cancer Specialists (C)"
                        # We'll parse:
                        #   - author name: everything up to the first comma
                        #   - institution: everything after the comma, minus any trailing (C)
                        author = chunk
                        institution = ""

                        # Attempt to split by the first comma
                        if ',' in chunk:
                            parts = chunk.split(',', 1)  # 1 split only
                            author = parts[0].strip()       # e.g. "Robert Weaver"
                            institution = parts[1].strip()  # e.g. "Florida Cancer Specialists (C)"

                            # remove trailing (C) if present
                            institution = re.sub(r'\(C\)', '', institution).strip()

                        # Our final disclosure string
                        # e.g. "Employment or Leadership: Florida Cancer Specialists"
                        # We only append the institution if it's not empty
                        if institution:
                            disc = f"{label_clean} {institution}"
                        else:
                            disc = label_clean  # fallback if we didn't parse an institution

                        all_disclosures.append({
                            "Author": author,
                            "Disclosures": [disc]
                        })

    return all_disclosures