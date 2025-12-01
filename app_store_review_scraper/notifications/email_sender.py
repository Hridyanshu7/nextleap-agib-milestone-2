import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
import os
import tempfile

class EmailSender:
    """
    A class to handle email notifications for review summaries.
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        Initialize the Email Sender.
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
            username (str): Email username
            password (str): Email password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)
    
    def create_html_report(self, summary: Dict, app_name: str) -> str:
        """
        Create an HTML email report from summary data.
        
        Args:
            summary (Dict): Summary data from ReviewAnalyzer
            app_name (str): Name of the app
            
        Returns:
            str: HTML formatted email content
        """
        # Sentiment distribution
        sentiment_rows = ""
        for sentiment, count in summary.get('sentiment_distribution', {}).items():
            emoji = "😊" if sentiment == "positive" else ("😐" if sentiment == "neutral" else "😞")
            sentiment_rows += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{emoji} {sentiment.capitalize()}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{count}</td>
                </tr>
            """
        # Top keywords
        keyword_items = ""
        for keyword, count in summary.get('top_keywords', [])[:10]:
            keyword_items += f"<li><strong>{keyword}</strong>: {count} mentions</li>"
        
        # Top Themes
        theme_items = ""
        for theme, count in summary.get('top_themes', [])[:3]:
            theme_items += f"<li><strong>{theme}</strong>: {count} mentions</li>"

        # User Quotes
        quote_items = ""
        for quote in summary.get('user_quotes', [])[:3]:
            quote_items += f"<li><em>\"{quote}\"</em></li>"

        # Action Ideas
        action_items = ""
        for action in summary.get('action_ideas', [])[:3]:
            action_items += f"<li>{action}</li>"

        # Critical reviews (using safe_text if available)
        critical_reviews = ""
        for review in summary.get('recent_critical_reviews', [])[:5]:
            date_str = review['review_date'].strftime('%Y-%m-%d %H:%M') if hasattr(review['review_date'], 'strftime') else str(review['review_date'])
            stars = "⭐" * review['rating']
            text = review.get('safe_text', review.get('review_text', ''))
            critical_reviews += f"""
                <div style="margin-bottom: 15px; padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <div style="margin-bottom: 5px;">
                        <strong>{stars}</strong> - <em>{date_str}</em>
                    </div>
                    <div>{text[:200]}{'...' if len(text) > 200 else ''}</div>
                </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-left: 4px solid #667eea;
                }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                .section-title {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-top: 30px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 App Review Summary Report</h1>
                <p><strong>App:</strong> {app_name}</p>
                <p><strong>Report Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class="metric-card">
                <h3>Key Metrics</h3>
                <div style="display: flex; justify-content: space-around; margin-top: 20px;">
                    <div style="text-align: center;">
                        <div class="metric-value">{summary.get('total_reviews', 0)}</div>
                        <div>Total Reviews</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="metric-value">{summary.get('average_rating', 0)}</div>
                        <div>Average Rating</div>
                    </div>
                </div>
            </div>

            <h2 class="section-title">🔥 Top 3 Themes</h2>
            <ul style="list-style-type: none; padding: 0;">
                {theme_items if theme_items else "<li>No significant themes detected.</li>"}
            </ul>

            <h2 class="section-title">💡 Action Ideas</h2>
            <ul style="list-style-type: none; padding: 0;">
                {action_items if action_items else "<li>No specific actions identified.</li>"}
            </ul>

            <h2 class="section-title">🗣️ User Quotes</h2>
            <ul style="list-style-type: none; padding: 0;">
                {quote_items if quote_items else "<li>No quotes available.</li>"}
            </ul>
            
            <h2 class="section-title">😊 Sentiment Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sentiment</th>
                        <th style="text-align: center;">Count</th>
                    </tr>
                </thead>
                <tbody>
                    {sentiment_rows}
                </tbody>
            </table>
            
            <h2 class="section-title">🔑 Top Keywords</h2>
            <ul style="list-style-type: none; padding: 0;">
                {keyword_items}
            </ul>
            
            <h2 class="section-title">⚠️ Recent Critical Reviews</h2>
            {critical_reviews if critical_reviews else "<p>No critical reviews in this period.</p>"}
            
            <div style="margin-top: 40px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center;">
                <p style="color: #666; margin: 0;">This is an automated report generated by the App Review Scraper</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, recipients: List[str], subject: str, html_content: str, attachment_path: Optional[str] = None) -> bool:
        """
        Send an email to recipients.
        
        Args:
            recipients (List[str]): List of recipient email addresses
            subject (str): Email subject
            html_content (str): HTML content of the email
            attachment_path (str, optional): Path to file to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
                    self.logger.info(f"Attached file: {os.path.basename(attachment_path)}")
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def format_date_range(self, days: int) -> str:
        """
        Format date range for subject line.
        
        Args:
            days (int): Number of days back from today
            
        Returns:
            str: Formatted date range string like "24th Nov'25 to 30th Nov'25"
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        def format_date_with_suffix(dt: datetime) -> str:
            day = dt.day
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            month_year = dt.strftime("%b'%y")
            return f"{day}{suffix} {month_year}"
        
        return f"{format_date_with_suffix(start_date)} to {format_date_with_suffix(end_date)}"
    
    def create_excel_attachment(self, reviews_df: pd.DataFrame, app_name: str) -> str:
        """
        Create an Excel file with review data.
        
        Args:
            reviews_df (pd.DataFrame): DataFrame containing reviews
            app_name (str): Name of the app
            
        Returns:
            str: Path to the created Excel file
        """
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reviews_{app_name.replace(' ', '_')}_{timestamp}.xlsx"
        filepath = os.path.join(temp_dir, filename)
        
        # Select relevant columns for export
        export_columns = [
            'review_date', 'source', 'user_name', 'rating', 'review_text',
            'sentiment', 'sentiment_score', 'app_version', 'developer_reply',
            'reply_date', 'device'
        ]
        
        # Filter to only existing columns
        available_columns = [col for col in export_columns if col in reviews_df.columns]
        export_df = reviews_df[available_columns].copy()
        
        # Format dates for Excel
        for col in ['review_date', 'reply_date']:
            if col in export_df.columns:
                export_df[col] = pd.to_datetime(export_df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create Excel file with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            export_df.to_excel(writer, sheet_name='Reviews', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Reviews']
            for idx, col in enumerate(export_df.columns):
                max_length = max(
                    export_df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        self.logger.info(f"Created Excel file: {filepath}")
        return filepath
    
    def send_summary_report(self, summary: Dict, app_name: str, recipients: List[str], 
                          reviews_df: Optional[pd.DataFrame] = None, days: int = 7) -> bool:
        """
        Send a summary report email with Excel attachment.
        
        Args:
            summary (Dict): Summary data from ReviewAnalyzer
            app_name (str): Name of the app
            recipients (List[str]): List of recipient email addresses
            reviews_df (pd.DataFrame, optional): DataFrame with all reviews for Excel attachment
            days (int): Number of days covered in the report
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Format subject with date range
        date_range = self.format_date_range(days)
        subject = f"📊 Weekly App Review Summary [{date_range}] - {app_name}"
        
        # Create HTML content
        html_content = self.create_html_report(summary, app_name)
        
        # Create Excel attachment if reviews data provided
        attachment_path = None
        if reviews_df is not None and not reviews_df.empty:
            try:
                attachment_path = self.create_excel_attachment(reviews_df, app_name)
            except Exception as e:
                self.logger.error(f"Error creating Excel attachment: {str(e)}")
        
        # Send email
        result = self.send_email(recipients, subject, html_content, attachment_path)
        
        # Clean up temporary file
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.remove(attachment_path)
                self.logger.info(f"Cleaned up temporary file: {attachment_path}")
            except Exception as e:
                self.logger.warning(f"Could not delete temporary file: {str(e)}")
        
        return result
