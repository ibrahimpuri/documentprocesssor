import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Example usage
text = "Invoice Number: 12345 Date: 2024-07-15 Customer Name: John Doe Address: 123 Elm Street, Springfield, IL, 62701"
entities = extract_entities(text)
print(entities)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_documents_with_logging(documents, processor):
    processed_data = defaultdict(list)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for doc in documents:
            content = preprocess_text(doc['content'])
            try:
                if doc['type'] == 'invoice':
                    futures.append(executor.submit(processor.extract_invoice_info, content))
                elif doc['type'] == 'medical_report':
                    futures.append(executor.submit(processor.extract_medical_report_info, content))
                elif doc['type'] == 'news_article':
                    futures.append(executor.submit(processor.extract_news_article_info, content))
            except Exception as e:
                logging.error(f"Error processing document {doc['type']}: {e}")

        for future in futures:
            try:
                result = future.result()
                if 'Invoice Number' in result:
                    processed_data['invoices'].append(result)
                elif 'Patient Name' in result:
                    for pres in result['Prescriptions']:
                        pres['Drug Info'] = fetch_drug_info(pres['Drug'])
                    processed_data['medical_reports'].append(result)
                elif 'Title' in result:
                    processed_data['news_articles'].append(result)
            except Exception as e:
                logging.error(f"Error in future result: {e}")

    return processed_data

