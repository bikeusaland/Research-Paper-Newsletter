# createEmailSummary.py
from datetime import datetime
from typing import List
from getPapers import Article

def create_email_summary(articles: List[Article]) -> str:
    """Create formatted HTML summary of articles"""
    
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
        <h1>ArXiv AI Papers Daily Summary</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """
    
    for article in articles:
        html_content += f"""
        <div class="article">
            <div class="title">{article.title}</div>
            <div class="links">
                <a href="{article.pdf_link}">PDF</a>
                <a href="{article.abstract_link}">Abstract</a>
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
    
    with open("finalSummary.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_content
