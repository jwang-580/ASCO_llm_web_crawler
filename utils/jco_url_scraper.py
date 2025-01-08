from paperscraper.pubmed import get_and_dump_pubmed_papers
import os
import json

jco_paper_query = ['"journal of clinical oncology official journal of the american society of clinical oncology"[Journal]', 
                   '2000/01/01:2025/01/01[Date - Publication]',
                   '"clinical trial"[Publication Type]']

if os.path.exists('data/jco_papers.jsonl'):
    print('jco_papers.jsonl already exists')
else:
    get_and_dump_pubmed_papers(jco_paper_query, output_filepath='data/jco_papers.jsonl')

if os.path.exists('data/jco_urls.jsonl'):
    print('jco_urls.jsonl already exists')
else:
    # load jco_papers.jsonl, extract the value of key 'doi'
    dois = []
    urls = []
    with open('data/jco_papers.jsonl', 'r') as file:
        for line in file:
            try:
                # Get the DOI, handle None values
                doi_raw = json.loads(line).get('doi')
                if doi_raw is None:
                    print(f"Warning: DOI is None in line: {line.strip()}")
                    continue
                    
                doi = doi_raw.split('\n')[0].strip()
                
                if doi.startswith('10.1200/JCO'):
                    dois.append(doi)
                    url = f"https://ascopubs.org/doi/{doi}"
                    urls.append(url)
                else:
                    print(f"Skipping non-JCO DOI: {doi}")
                    
            except KeyError:
                print(f"Warning: No DOI found in line: {line.strip()}")
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON in line: {line.strip()}")

        with open('data/jco_urls.jsonl', 'w') as file:
            for url in urls:
                file.write(json.dumps({'url': url}) + '\n')