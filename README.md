# SNP Literature Information Fetcher

This script fetches literature information for a given list of SNP IDs using NCBI E-utilities, processes the information to extract diseases mentioned in the titles and abstracts, and summarizes the relevance of each SNP variant. The summarized information is saved to a CSV file.

## Requirements

- Python 3.8+
- `requests` library
- `beautifulsoup4` library
- `pandas` library
- `spacy` library
- `nltk` library
- `lxml` parser

## Setup

1. Create a new conda environment:

   ```bash
   conda create -n variant_analysis python=3.8
   conda activate variant_analysis
   pip install requests beautifulsoup4 pandas spacy nltk lxml
   python -m spacy download en_core_web_sm

   chmod +x run.sh
   ./run.sh ./data/input.txt ./data/output.csv

## Main Functionality
1.  **Fetch Literature Information:**

The script fetches literature information for each SNP ID using the NCBI E-utilities API. It sends a search request to obtain the PubMed IDs (PMIDs) and then fetches the details of each publication.

2.  **Extract Diseases from Text:**

The script uses spaCy's NLP model to extract diseases mentioned in the titles and abstracts of the publications. It identifies entities labeled as "DISEASE" or "CONDITION" and also looks for specific keywords related to diseases.

3. **Summarize Relevance:**

For each SNP ID, the script summarizes the relevance based on the diseases mentioned in the titles and abstracts. It categorizes the relevance as "High" if any diseases are mentioned; otherwise, it categorizes it as "Low".

4. **Save to CSV:**

The summarized information is saved to a CSV file.
