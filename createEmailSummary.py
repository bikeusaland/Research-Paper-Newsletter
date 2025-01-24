# createEmailSummary.py
from datetime import datetime
from typing import List
from getPapers import Article

def create_email_summary(articles: List[Article], pdf_folder: str = None, output_path: str = "finalSummary.html") -> str:
    """Create formatted HTML summary of articles"""
    
    # Set title based on whether we're processing local PDFs or ArXiv papers
    title = f"Local Papers in {pdf_folder} Summary" if pdf_folder else "ArXiv AI Papers Daily Summary"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; }}
            .article {{ margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }}
            .title {{ color: #2c5282; font-size: 18px; font-weight: bold; }}
            .links {{ margin: 10px 0; }}
            .links a {{ color: #4299e1; text-decoration: none; margin-right: 15px; }}
            .summary {{ line-height: 1.6; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """
    
    for article in articles:
        # Only show PDF link if it exists
        pdf_link_html = f'<a href="{article.pdf_link}">PDF</a>' if article.pdf_link else ''
        # Only show Abstract link if it exists
        abstract_link_html = f'<a href="{article.abstract_link}">Abstract</a>' if article.abstract_link else ''
        
        html_content += f"""
        <div class="article">
            <div class="title">{article.title}</div>
            <div class="links">
                {pdf_link_html}
                {abstract_link_html}
            </div>
            <div class="summary">
                <p>{article.summary}</p>
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_content
