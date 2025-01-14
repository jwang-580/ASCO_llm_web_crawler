# use OpenAI structured output to identify the pharma/biotech company based on the abstract

from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import pandas as pd
from datetime import datetime
import ast

load_dotenv()
client = OpenAI(api_key=os.getenv('OAI_API_KEY'))

asco_articles = pd.read_csv('data/asco_articles.csv')

class Company(BaseModel):
    product_name: str
    company_name: str
    company_in_the_list: bool

for index, study in asco_articles.iterrows():
    abstract = study['abstract']
    year = study['publication_date']
    coi_company = set()

    # Parse the string to list of dictionaries using ast.literal_eval
    try:
        disclosures = ast.literal_eval(study['author_disclosures'])
    except (ValueError, SyntaxError) as e:
        print(f"Warning: Could not parse author disclosures for row {index}")
        print(f"Error details: {str(e)}")
        continue

    for disclosure in disclosures:
        if disclosure['Author'] == 'None':
            continue
            
        for disc in disclosure['Disclosures']:
            # Remove the category label (everything before the colon)
            if ':' in disc:
                disc = disc.split(':', 1)[1]
                
            # Split on commas and add to set
            companies = [c.strip().replace('(Inst)', '').strip() for c in disc.split(',')]
            coi_company.update(c for c in companies if c and c != 'No other potential conflicts of interest were reported.')

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-11-20",
        messages=[
            {"role": "system", "content": "You are an expert in medical oncology."},
            {"role": "user", "content": f'''You are provided with an abstract of a study, identify the medical product (e.g. drug, device) that is being studied and return the generic name(e.g. imatinib). If the study is not about a medical product, return 'N/A'. If multiple products are studied, focus on the primary one. 
            Next, a list of commercial company names is provided, which may or may not contain the company that produces the product being studied. Based on your own knowledge, return the name of the commercial company (usally a pharma/biotech/manufacturing company) that produces this product exclusively at the time of the study publication. If multiple companies can produce the same product, which usually happens in the case of a none-proprietary drug, return 'N/A' for the company name. If you are not sure about the company name, return 'unsure'.
            The abstract: {abstract} 
            Publication time: {str(year)}
            List of companies: {coi_company}'''},
        ],
        response_format=Company,
    )
    company_output = completion.choices[0].message.parsed
    # print(coi_company)
    print(company_output)
    asco_articles.at[index, 'product_name'] = company_output.product_name
    asco_articles.at[index, 'company_name'] = company_output.company_name
    asco_articles.at[index, 'company_in_the_list'] = company_output.company_in_the_list

# save results based on current time stamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
asco_articles.to_csv(f'results/asco_articles_with_company_{timestamp}.csv', index=False)
