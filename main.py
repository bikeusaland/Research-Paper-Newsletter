from getPapers import Article, get_new_papers
from createSummaries import create_summaries
import logging
from typing import List
import os
from datetime import datetime
from createEmailSummary import create_email_summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_papers(url: str) -> List[Article]:
    """Main function to fetch and process papers"""
    try:
        papers = get_new_papers(url)
        logging.info(f"Found {len(papers)} papers")
        
        for paper in papers:
            logging.info(f"\nProcessing: {paper.title}")
            print(f"Title: {paper.title}")
            print(f"PDF Link: {paper.pdf_link}")
            print(f"Abstract: {paper.abstract_link}")
            print(f"Content: {paper.pdf_content}")
            print("-" * 80)
        return papers
    except Exception as e:
        logging.error(f"Error processing papers: {e}")
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
    """Process papers and send email summary"""
    try:
        newArticles = process_papers(url)
        if not newArticles:
            logging.warning("No articles found to process")
            return
            
        finalArticles = create_summaries(newArticles)
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
    
    # Run as if it were a cloud function
    cloud_function(None, None)
