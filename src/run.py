import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from time import sleep

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

# Function to fetch literature information for a given SNP ID using NCBI E-utilities
def fetch_literature_info(snp_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={snp_id}&retmode=json"
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&retmode=xml&id="

    search_response = requests.get(search_url)
    search_data = search_response.json()

    if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
        id_list = search_data['esearchresult']['idlist']
        if not id_list:
            return [{'SNP ID': snp_id, 'PMID': 'N/A', 'Title': 'N/A', 'Abstract': 'N/A', 'Diseases': 'N/A'}]
        
        pmid_list = ','.join(id_list)
        fetch_response = requests.get(f"{fetch_url}{pmid_list}")
        fetch_soup = BeautifulSoup(fetch_response.content, 'lxml')

        articles = []
        for article in fetch_soup.find_all('PubmedArticle'):
            pmid = article.PMID.text if article.PMID else 'N/A'
            title = article.ArticleTitle.text if article.ArticleTitle else 'N/A'
            abstract = article.Abstract.AbstractText.text if article.Abstract and article.Abstract.AbstractText else 'N/A'
            diseases = extract_diseases_from_text(abstract)
            articles.append({'SNP ID': snp_id, 'PMID': pmid, 'Title': title, 'Abstract': abstract, 'Diseases': diseases})
        
        return articles
    else:
        return [{'SNP ID': snp_id, 'PMID': 'N/A', 'Title': 'N/A', 'Abstract': 'N/A', 'Diseases': 'N/A'}]

# Function to extract diseases from text using simple keyword matching
def extract_diseases_from_text(text):
    if not text:
        return 'N/A'
    
    disease_keywords = ['cancer', 'tumor', 'disease', 'syndrome', 'disorder', 'condition']
    diseases = set()

    for keyword in disease_keywords:
        if keyword in text.lower():
            diseases.add(keyword)
    
    return ', '.join(diseases) if diseases else 'N/A'

# Function to summarize SNP information
def summarize_snp_info(data):
    summaries = []

    for index, row in data.iterrows():
        snp_id = row['SNP ID']
        pmid = row['PMID']
        title = row['Title']
        abstract = row['Abstract']
        
        diseases_in_title, title_sentences = extract_diseases_from_text(title)
        diseases_in_abstract, abstract_sentences = extract_diseases_from_text(abstract)
        
        all_diseases = diseases_in_title.union(diseases_in_abstract)
        all_sentences = title_sentences + abstract_sentences
        
        relevance = "High" if len(all_diseases) > 0 else "Low"
        summary = {
            'SNP ID': snp_id,
            'PMID': pmid,
            'Title': title,
            'Abstract': abstract,
            'Diseases Mentioned': ', '.join(all_diseases),
            'Relevant Sentences': ' '.join(all_sentences),
            'Relevance': relevance
        }
        summaries.append(summary)

    return pd.DataFrame(summaries)

# Main function to read input file, fetch literature information, and save the summarized information
def main(input_file, output_dir):
    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Initialize a list to hold the results
    results = []

    for line in lines:
        snp_id = line.strip()
        if not snp_id:
            continue

        articles = fetch_literature_info(snp_id)
        results.extend(articles)
        sleep(1)  # Adding a delay to respect NCBI's usage policy

    # Convert the results list to a DataFrame
    df = pd.DataFrame(results)

    # Remove the 'Diseases' column if it exists
    if 'Diseases' in df.columns:
        df.drop('Diseases', inplace=True, axis=1)

    # Convert PMID column to string and remove '.0'
    df['PMID'] = df['PMID'].astype(str).str.replace('.0', '', regex=False)

    # Replace NaN values in 'Title' and 'Abstract' columns with empty strings
    df['Title'] = df['Title'].fillna('')
    df['Abstract'] = df['Abstract'].fillna('')

    # Summarize the relevance of each SNP variant
    summary_df = summarize_snp_info(df)

    # Save the summary to a new CSV file
    output_file = os.path.join(output_dir, "snp_disease_summary.csv")
    summary_df.to_csv(output_file, index=False)

    print(f"Summary saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    main(input_file, output_dir)
