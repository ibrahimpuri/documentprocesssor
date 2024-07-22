import re
import spacy
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Sample documents
documents = [
    {
        "type": "invoice",
        "content": """
        Invoice Number: 12345
        Date: 2024-07-15
        Customer Name: John Doe
        Address: 123 Elm Street, Springfield, IL, 62701
        Items:
          - Widget A: $50.00
          - Widget B: $30.00
          - Widget C: $20.00
        Total Amount: $100.00
        """
    },
    {
        "type": "medical_report",
        "content": """
        Patient Name: Jane Smith
        Date of Birth: 1985-05-10
        Date of Visit: 2024-07-18
        Diagnosis: Acute Bronchitis
        Prescriptions:
          - Amoxicillin: 500mg, twice daily for 7 days
          - Cough Syrup: 10ml, as needed
        Recommendations:
          - Rest and hydrate
          - Follow up in 1 week
        """
    },
    {
        "type": "news_article",
        "content": """
        Title: Breakthrough in Renewable Energy Technology
        Date: 2024-07-17
        Author: Sarah Johnson
        Summary: Scientists at the National Renewable Energy Laboratory have developed a new type of solar cell that significantly improves energy conversion efficiency. This breakthrough could lead to more affordable and efficient solar panels, potentially transforming the renewable energy landscape.
        Key Points:
          - New solar cell technology
          - Increased energy conversion efficiency
          - Potential for affordable solar panels
          - Impact on renewable energy industry
        """
    }
]

def preprocess_text(text):
    return text.strip()

class DocumentProcessor:
    def __init__(self, nlp):
        self.nlp = nlp

    def extract_invoice_info(self, text):
        info = {}
        info['Invoice Number'] = self._extract_with_regex(r'Invoice Number:\s*(.*)', text)
        info['Date'] = self._extract_with_regex(r'Date:\s*(.*)', text)
        info['Customer Name'] = self._extract_with_regex(r'Customer Name:\s*(.*)', text)
        info['Address'] = self._extract_with_regex(r'Address:\s*(.*)', text)
        items = re.findall(r'- (.*): \$(.*)', text)
        info['Items'] = [{'Item': item[0], 'Price': float(item[1])} for item in items]
        info['Total Amount'] = float(self._extract_with_regex(r'Total Amount:\s*\$(.*)', text))
        return info

    def extract_medical_report_info(self, text):
        info = {}
        info['Patient Name'] = self._extract_with_regex(r'Patient Name:\s*(.*)', text)
        info['Date of Birth'] = self._extract_with_regex(r'Date of Birth:\s*(.*)', text)
        info['Date of Visit'] = self._extract_with_regex(r'Date of Visit:\s*(.*)', text)
        info['Diagnosis'] = self._extract_with_regex(r'Diagnosis:\s*(.*)', text)
        prescriptions = re.findall(r'- (.*): (.*)', text)
        info['Prescriptions'] = [{'Drug': pres[0], 'Dosage': pres[1]} for pres in prescriptions]
        recommendations = re.findall(r'- (.*)', text.split('Recommendations:')[1])
        info['Recommendations'] = recommendations
        return info

    def extract_news_article_info(self, text):
        info = {}
        info['Title'] = self._extract_with_regex(r'Title:\s*(.*)', text)
        info['Date'] = self._extract_with_regex(r'Date:\s*(.*)', text)
        info['Author'] = self._extract_with_regex(r'Author:\s*(.*)', text)
        info['Summary'] = self._extract_with_regex(r'Summary:\s*(.*)', text)
        key_points = re.findall(r'- (.*)', text.split('Key Points:')[1])
        info['Key Points'] = key_points
        return info

    def _extract_with_regex(self, pattern, text):
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None

def fetch_drug_info(drug_name):
    api_url = f"https://api.fda.gov/drug/label.json?search={drug_name}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json().get('results', [{}])[0].get('description', 'No information available')
    return 'No information available'

def process_documents(documents, processor):
    processed_data = defaultdict(list)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for doc in documents:
            content = preprocess_text(doc['content'])
            if doc['type'] == 'invoice':
                futures.append(executor.submit(processor.extract_invoice_info, content))
            elif doc['type'] == 'medical_report':
                futures.append(executor.submit(processor.extract_medical_report_info, content))
            elif doc['type'] == 'news_article':
                futures.append(executor.submit(processor.extract_news_article_info, content))

        for future in futures:
            result = future.result()
            if 'Invoice Number' in result:
                processed_data['invoices'].append(result)
            elif 'Patient Name' in result:
                for pres in result['Prescriptions']:
                    pres['Drug Info'] = fetch_drug_info(pres['Drug'])
                processed_data['medical_reports'].append(result)
            elif 'Title' in result:
                processed_data['news_articles'].append(result)

    return processed_data

processor = DocumentProcessor(nlp)
processed_data = process_documents(documents, processor)

# Display the processed data
print(json.dumps(processed_data, indent=2))

# Example Analysis and Visualization
def analyze_data(processed_data):
    # Example: Analysis on Invoices
    invoice_amounts = [invoice['Total Amount'] for invoice in processed_data['invoices']]
    plt.figure(figsize=(10, 6))
    sns.histplot(invoice_amounts, bins=10, kde=True)
    plt.title('Distribution of Invoice Amounts')
    plt.xlabel('Invoice Amount ($)')
    plt.ylabel('Frequency')
    plt.show()

    # Example: Analysis on Medical Reports
    diagnoses = [report['Diagnosis'] for report in processed_data['medical_reports']]
    diagnosis_counts = defaultdict(int)
    for diagnosis in diagnoses:
        diagnosis_counts[diagnosis] += 1
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(diagnosis_counts.keys()), y=list(diagnosis_counts.values()))
    plt.title('Diagnosis Frequency')
    plt.xlabel('Diagnosis')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.show()

    # Advanced Visualization with Plotly
    fig = px.histogram(invoice_amounts, nbins=10, title='Distribution of Invoice Amounts')
    fig.update_layout(xaxis_title='Invoice Amount ($)', yaxis_title='Frequency')
    fig.show()

analyze_data(processed_data)