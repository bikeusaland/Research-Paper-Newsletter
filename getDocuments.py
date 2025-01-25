import requests
import pdfplumber
import tempfile
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass
import os
import shutil
import logging

@dataclass
class Article:
    title: str
    pdf_link: str
    abstract_link: str
    article_id: str
    pdf_content: str  # Keep as pdf_content instead of local_path to match existing class

def extract_pdf_content(pdf_url: str) -> str:
    """Downloads and extracts text content from PDF"""
    try:
        # Download PDF to temporary file
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
            
        # Extract text from PDF
        text_content = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
                
        # Cleanup temp file
        os.unlink(tmp_path)
        return text_content.strip()
        
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
        return ""

def setup_documents_dir(documents_dir: str = "documents") -> str:
    """Creates/cleans documents directory"""
    if os.path.exists(documents_dir):
        shutil.rmtree(documents_dir)
    os.makedirs(documents_dir)
    print(f"Created documents dir at: {os.path.abspath(documents_dir)}")
    print(f"Directory is writable: {os.access(documents_dir, os.W_OK)}")
    return documents_dir

def get_new_documents(url: str, documents_dir: str = "documents") -> List[Article]:
    documents_dir = setup_documents_dir(documents_dir)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        article_elements = soup.find('dl', id='articles')
        
        if not article_elements:
            logging.warning("No articles found")
            return []
            
        entries = article_elements.find_all(['dt', 'dd'])
        
        for i in range(0, len(entries), 2):
            try:
                dt = entries[i]
                dd = entries[i+1]
                
                article_id = dt.find('a', {'title': 'Abstract'}).text.strip()
                abstract_link = f"https://arxiv.org/abs/{article_id}"
                pdf_link = f"https://arxiv.org/pdf/{article_id}"
                
                title = dd.find('div', class_='list-title').text
                title = title.replace('Title:', '').strip()
                
                # Clean article_id by removing "arXiv:" prefix
                article_id = article_id.replace('arXiv:', '')
                filename = f"{article_id}.pdf"
                filepath = os.path.join(documents_dir, filename)
                
                # Download PDF with proper headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/pdf'
                }
                
                logging.info(f"Downloading PDF for {article_id}")
                
                print(f"Attempting to save PDF to: {filepath}")

                pdf_response = requests.get(
                    pdf_link, 
                    headers=headers,
                    stream=True,
                    verify=True,
                    timeout=30
                )
                
                # Verify PDF response
                if pdf_response.status_code != 200:
                    logging.error(f"Failed to download PDF: {pdf_response.status_code}")
                    raise Exception(f"PDF download failed with status {pdf_response.status_code}")

                if 'application/pdf' not in pdf_response.headers.get('content-type', ''):
                    logging.error("Response is not a PDF")
                    raise Exception("Response is not a PDF")

                # Save PDF with progress logging
                with open(filepath, 'wb') as f:
                    total_size = int(pdf_response.headers.get('content-length', 0))
                    block_size = 8192
                    wrote = 0
                    for chunk in pdf_response.iter_content(chunk_size=block_size):
                        if chunk:
                            wrote += len(chunk)
                            f.write(chunk)
                    if total_size != 0 and wrote != total_size:
                        raise Exception("Downloaded file size doesn't match expected size")

                # Verify downloaded file
                if not os.path.exists(filepath):
                    raise Exception(f"File not created at {filepath}")
                if os.path.getsize(filepath) == 0:
                    os.remove(filepath)
                    raise Exception("Downloaded file is empty")
                
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    logging.info(f"Successfully saved {filename}")
                    relative_path = filepath
                else:
                    logging.error(f"Failed to save {filename}")
                    continue
                
                article = Article(
                    title=title,
                    pdf_link=pdf_link,
                    abstract_link=abstract_link,
                    article_id=article_id,
                    pdf_content=relative_path
                )
                
                articles.append(article)
                
            except Exception as e:
                logging.error(f"Error processing article {article_id if 'article_id' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return articles
        
    except Exception as e:
        logging.error(f"Error fetching documents: {str(e)}")
        return []

print(f"Documents directory exists: {os.path.exists('documents')}")
print(f"Current working directory: {os.getcwd()}")
