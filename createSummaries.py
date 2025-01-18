import os
import logging
from typing import List
from openai import OpenAI
from getPapers import Article
from dataclasses import dataclass
import PyPDF2

@dataclass
class Article:
    title: str
    pdf_link: str 
    abstract_link: str
    article_id: str
    pdf_content: str
    summary: str = "" 

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text[:4000]  # Truncate to fit token limits
    except Exception as e:
        logging.error(f"Error extracting PDF text: {e}")
        return ""

def create_summaries(articles: List[Article]) -> List[Article]:
    """Generate summaries for articles using OpenAI Chat API"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    system_prompt = """You are a research assistant that provides concise summaries of academic papers.
    Focus on:
    1. Key findings and contributions
    2. Methodology and approach
    3. Main conclusions and implications
    4. Respond with a basic string, no formatting, titles, heading etc. is required."""
    
    for article in articles:
        try:
            if not os.path.exists(article.pdf_content):
                logging.error(f"PDF not found: {article.pdf_content}")
                continue
            
            # Extract PDF text
            pdf_text = extract_pdf_text(article.pdf_content)
            if not pdf_text:
                continue
                
            # Create completion request
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""Please summarize this paper:
                    Title: {article.title}
                    Content: {pdf_text}"""}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            article.summary = response.choices[0].message.content
            logging.info(f"Generated summary for: {article.title}")
            
        except Exception as e:
            logging.error(f"Error processing {article.title}: {str(e)}")
            article.summary = ""
            
    return articles