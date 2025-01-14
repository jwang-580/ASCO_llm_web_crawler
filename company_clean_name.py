# A company can have multiple forms of name, such as Eli Lilly/Lilly, etc.
# This script use LLM to identify all the forms of name for a company for an entity

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

asco_articles_with_company = pd.read_csv('results/asco_articles_with_company_human_edited.csv')
asco_articles_with_company['company_name_variants'] = None

class CompanyNameVariants(BaseModel):
    company_name_variants: list[str]

for index, study in asco_articles_with_company.iterrows():
    
    company_name = study['company_name']
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
            {"role": "user", "content": f'''You are given a company name. You are then provided with a list of biotech/pharma companies which may or may not contain this company. If the list includes this company, please identify all the forms of name for this company in the list, and return them.
            The company name: {company_name} 
            List of companies: {coi_company}'''},
        ],
        response_format=CompanyNameVariants,
    )
    company_output = completion.choices[0].message.parsed
    # print(coi_company)
    print(company_output)
    # Use loc instead of at for setting values
    asco_articles_with_company.loc[index, 'company_name_variants'] = str(company_output.company_name_variants)

# save results based on current time stamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
asco_articles_with_company.to_csv(f'results/asco_articles_with_company_name_variants_{timestamp}.csv', index=False)
