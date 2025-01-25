import logging
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Parse arguments first to set up logging before any imports
parser = argparse.ArgumentParser(description='Process ArXiv papers or local PDFs')
parser.add_argument('--pdfs', type=str, help='Path to folder containing PDF files to process')
parser.add_argument('--documents', type=str, help='Override default documents directory for downloads', default="documents")
parser.add_argument('--output', type=str, help='Path for the output HTML summary', default="finalSummary.html")
parser.add_argument('--llm', choices=['local', "fuelix", 'openai', 'ollama'], default='openai',
                  help='Choose LLM backend: local (LM Studio), fuelix, openai, or ollama')
parser.add_argument('--debug', action='store_true', help='Enable debug logging')
args = parser.parse_args()

# Configure logging before any imports
logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from getDocuments import get_new_documents
from createSummaries import create_summaries, Article
from typing import List
from datetime import datetime
from createEmailSummary import create_email_summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import glob

def process_local_pdfs(pdf_folder: str) -> List[Article]:
    """Process PDFs from a local folder"""
    articles = []
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    for pdf_path in pdf_files:
        try:
            filename = os.path.basename(pdf_path)
            article_id = os.path.splitext(filename)[0]
            
            # Convert to absolute path for the PDF link
            abs_path = os.path.abspath(pdf_path)
            file_url = f"file://{abs_path}"
            
            article = Article(
                title=article_id,  # Using filename as title since we don't have metadata
                pdf_link=file_url,  # Use file:// URL for local files
                abstract_link="",  # Empty since it's local
                article_id=article_id,
                pdf_content=pdf_path  # Full path to PDF
            )
            articles.append(article)
            logging.info(f"Added local PDF: {pdf_path}")
            
        except Exception as e:
            logging.error(f"Error processing local PDF {pdf_path}: {e}")
            continue
            
    return articles

def process_documents(url: str) -> List[Article]:
    """Main function to fetch and process documents"""
    try:
        documents = get_new_documents(url)
        logging.info(f"Found {len(documents)} documents")
        
        for document in documents:
            logging.info(f"\nProcessing: {document.title}")
            print(f"Title: {document.title}")
            print(f"PDF Link: {document.pdf_link}")
            print(f"Abstract: {document.abstract_link}")
            print(f"Content: {document.pdf_content}")
            print("-" * 80)
        return documents
    except Exception as e:
        logging.error(f"Error processing documents: {e}")
        raise

def send_email(html_content: str) -> None:
    """Send email with the generated report"""
    # Get email configuration from environment variables
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        raise ValueError("Missing required environment variables for email configuration")
    
    msg = MIMEMultipart()
    msg['Subject'] = f'AI Papers Daily Summary - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise

def process_and_send_summary(url: str) -> None:
    """Process documents and send email summary"""
    try:
        newArticles = process_documents(url)
        if not newArticles:
            logging.warning("No articles found to process")
            return
            
        finalArticles = create_summaries(newArticles, llm=args.llm)
        if not finalArticles:
            logging.warning("No summaries generated")
            return
            
        html_content = create_email_summary(finalArticles)
        send_email(html_content)
        logging.info("Summary processed and email sent successfully")
        
    except Exception as e:
        logging.error(f"Error in process_and_send_summary: {e}")
        raise

def cloud_function(event, context):
    """Cloud Function entry point"""
    try:
        arxiv_url = os.environ.get('ARXIV_URL', "https://arxiv.org/list/cs.AI/new")
        process_and_send_summary(arxiv_url)
        return 'Success: Email sent'
    except Exception as e:
        error_msg = f"Error in cloud function: {str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)  # Cloud Functions will mark as failed

if __name__ == "__main__":

    # For local testing, set environment variables
    if not os.environ.get('SENDER_EMAIL'):
        os.environ['SENDER_EMAIL'] = ""
        os.environ['SENDER_PASSWORD'] = ""
        os.environ['RECEIVER_EMAIL'] = ""
    
    try:
        if args.pdfs:
            # Process local PDFs
            if not os.path.isdir(args.pdfs):
                raise ValueError(f"The path {args.pdfs} is not a valid directory")
                
            articles = process_local_pdfs(args.pdfs)
            if not articles:
                logging.warning("No PDFs found to process")
                exit(1)
                
            finalArticles = create_summaries(articles, llm=args.llm)
            if not finalArticles:
                logging.warning("No summaries generated")
                exit(1)
                
            html_content = create_email_summary(finalArticles, args.pdfs, args.output)
            send_email(html_content)
            logging.info("Summary processed and email sent successfully")
            
        else:
            # Update cloud_function to use the papers directory and LLM choice from args
            def cloud_function_with_papers_dir(event, context):
                try:
                    arxiv_url = os.environ.get('ARXIV_URL', "https://arxiv.org/list/cs.AI/new")
                    newArticles = get_new_documents(arxiv_url, args.documents)
                    if not newArticles:
                        logging.warning("No articles found to process")
                        return
                        
                    finalArticles = create_summaries(newArticles, llm=args.llm)
                    if not finalArticles:
                        logging.warning("No summaries generated")
                        return
                        
                    html_content = create_email_summary(finalArticles, output_path=args.output)
                    send_email(html_content)
                    logging.info("Summary processed and email sent successfully")
                    return 'Success: Email sent'
                except Exception as e:
                    error_msg = f"Error in cloud function: {str(e)}"
                    logging.error(error_msg)
                    raise Exception(error_msg)

            cloud_function_with_papers_dir(None, None)
            
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise
