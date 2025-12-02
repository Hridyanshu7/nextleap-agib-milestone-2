import streamlit as st
import pandas as pd
from datetime import datetime
import io
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_store_review_scraper.scrapers.google_play_scraper import GooglePlayScraper
from app_store_review_scraper.scrapers.app_store_scraper import AppStoreScraper
from app_store_review_scraper.analysis.summarizer import ReviewAnalyzer
from app_store_review_scraper.notifications.email_sender import EmailSender
from main import parse_play_url, lookup_apple_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download NLTK data
try:
    import nltk
    nltk.download('punkt')
    nltk.download('brown')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")

# Page configuration
st.set_page_config(
    page_title="App Review Scraper",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'reviews_df' not in st.session_state:
    st.session_state['reviews_df'] = None
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'app_name' not in st.session_state:
    st.session_state['app_name'] = None

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📱 App Review Scraper & Analyzer</h1>', unsafe_allow_html=True)
st.markdown("**Scrape, analyze, and get insights from Google Play Store and Apple App Store reviews**")

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

with st.sidebar:
    st.subheader("🔐 API Keys")
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get your free API key from: https://makersuite.google.com/app/apikey",
        placeholder="Enter your Gemini API key"
    )
    
    st.subheader("📊 Scraping Settings")
    scrape_days = st.number_input(
        "Days to scrape",
        min_value=1,
        max_value=90,
        value=7,
        help="Number of days of reviews to fetch"
    )
    
    max_reviews = st.number_input(
        "Maximum reviews",
        min_value=10,
        max_value=5000,
        value=5000,
        help="Maximum total reviews to fetch"
    )
    
    st.subheader("📧 Email Settings (Optional)")
    enable_email = st.checkbox("Enable email reports", value=False)
    
    if enable_email:
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        smtp_user = st.text_input("Email Address", placeholder="your-email@gmail.com")
        smtp_password = st.text_input("Email Password", type="password", help="Use App Password for Gmail")
        recipient_emails = st.text_area(
            "Recipient Emails (comma-separated)",
            placeholder="recipient1@example.com,recipient2@example.com"
        )

# Main content
tab1, tab2, tab3 = st.tabs(["📥 Scrape Reviews", "📊 Results", "ℹ️ About"])

with tab1:
    st.header("Enter App URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 Google Play Store")
        play_url = st.text_input(
            "Google Play Store URL",
            value="https://play.google.com/store/apps/details?id=com.nextbillion.groww&hl=en_IN",
            help="Example: https://play.google.com/store/apps/details?id=com.example.app"
        )
    
    with col2:
        st.subheader("🍎 Apple App Store")
        apple_url = st.text_input(
            "Apple App Store URL (Optional)",
            value="https://apps.apple.com/in/app/groww-stocks-mutual-fund-ipo/id1404871703",
            help="Example: https://apps.apple.com/us/app/example-app/id123456789"
        )
    
    st.markdown("---")
    
    # Scrape button
    if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
        
        # Validation
        if not play_url.strip():
            st.error("❌ Please enter a Google Play Store URL")
            st.stop()
        
        if not gemini_api_key:
            st.warning("⚠️ Gemini API key not provided. Analysis features will be limited.")
        
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            all_reviews = []
            
            # Parse Google Play URL
            status_text.text("🔍 Parsing Google Play URL...")
            progress_bar.progress(10)
            
            parsed_data = parse_play_url(play_url.strip())
            if not parsed_data or not parsed_data['package_name']:
                st.error("❌ Could not parse a valid Google Play package name from the URL.")
                st.stop()
            
            package_name = parsed_data['package_name']
            lang = parsed_data['lang']
            country = parsed_data['country']
            
            st.info(f"📦 Package: `{package_name}` | 🌍 Country: `{country}` | 🗣️ Language: `{lang}`")
            
            # Fetch Google Play reviews
            status_text.text("📱 Fetching Google Play reviews...")
            progress_bar.progress(20)
            
            gp_scraper = GooglePlayScraper(package_name, lang=lang, country=country)
            app_name = gp_scraper.get_app_name() or package_name
            
            st.success(f"✅ App Name: **{app_name}**")
            
            gp_reviews = gp_scraper.get_reviews(days=scrape_days, max_reviews=max_reviews)
            
            if not gp_reviews.empty:
                status_text.text("🧠 Analyzing Google Play reviews...")
                progress_bar.progress(40)
                
                analyzer = ReviewAnalyzer(gemini_api_key=gemini_api_key if gemini_api_key else None)
                gp_reviews['sentiment_score'] = gp_reviews['review_text'].apply(
                    lambda x: analyzer.analyze_sentiment(x)[1]
                )
                gp_reviews['sentiment'] = gp_reviews['sentiment_score'].apply(
                    lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
                )
                all_reviews.append(gp_reviews)
                st.success(f"✅ Fetched {len(gp_reviews)} Google Play reviews")
            else:
                st.warning("⚠️ No Google Play reviews found")
            
            # Apple App Store
            if apple_url.strip():
                status_text.text("🍎 Fetching Apple App Store reviews...")
                progress_bar.progress(60)
                
                import re
                id_match = re.search(r'id(\d+)', apple_url)
                country_match = re.search(r'apple\.com/([a-z]{2})/', apple_url)
                
                if id_match:
                    apple_id = id_match.group(1)
                    if country_match:
                        country = country_match.group(1)
                    
                    as_scraper = AppStoreScraper(country=country, app_name=app_name, app_id=apple_id)
                    as_reviews = as_scraper.fetch_reviews(count=max_reviews, days=scrape_days)
                    
                    if not as_reviews.empty:
                        status_text.text("🧠 Analyzing Apple reviews...")
                        progress_bar.progress(80)
                        
                        as_reviews['sentiment_score'] = as_reviews['review_text'].apply(
                            lambda x: analyzer.analyze_sentiment(x)[1]
                        )
                        as_reviews['sentiment'] = as_reviews['sentiment_score'].apply(
                            lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
                        )
                        all_reviews.append(as_reviews)
                        st.success(f"✅ Fetched {len(as_reviews)} Apple App Store reviews")
                    else:
                        st.warning("⚠️ No Apple App Store reviews found")
            
            # Combine and analyze
            if all_reviews:
                status_text.text("📊 Generating insights...")
                progress_bar.progress(90)
                
                combined_df = pd.concat(all_reviews, ignore_index=True)
                
                # Cap at max_reviews
                if len(combined_df) > max_reviews:
                    combined_df = combined_df.sort_values('review_date', ascending=False).head(max_reviews)
                
                # Store in session state
                st.session_state['reviews_df'] = combined_df
                st.session_state['app_name'] = app_name
                
                # Generate summary
                summary = analyzer.generate_summary(combined_df)
                st.session_state['summary'] = summary
                
                # Send email if enabled
                if enable_email and smtp_user and smtp_password and recipient_emails:
                    status_text.text("📧 Sending email report...")
                    try:
                        email_sender = EmailSender(smtp_server, smtp_port, smtp_user, smtp_password)
                        recipients = [e.strip() for e in recipient_emails.split(',') if e.strip()]
                        email_sender.send_summary_report(
                            summary=summary,
                            app_name=app_name,
                            recipients=recipients,
                            reviews_df=combined_df,
                            days=scrape_days
                        )
                        st.success("✅ Email report sent successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {str(e)}")
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                st.success("🎉 Scraping and analysis complete! Check the **Results** tab.")
                
            else:
                st.error("❌ No reviews fetched from any source")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Scraping error: {str(e)}", exc_info=True)

with tab2:
    st.header("📊 Analysis Results")
    
    if st.session_state.get('reviews_df') is None:
        st.info("👈 Start by scraping reviews in the **Scrape Reviews** tab")
    else:
        df = st.session_state['reviews_df']
        summary = st.session_state['summary']
        app_name = st.session_state['app_name']
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reviews", summary['total_reviews'])
        with col2:
            st.metric("Average Rating", f"{summary['average_rating']:.2f}")
        with col3:
            pos_count = summary['sentiment_distribution'].get('positive', 0)
            st.metric("Positive Reviews", pos_count)
        with col4:
            neg_count = summary['sentiment_distribution'].get('negative', 0)
            st.metric("Negative Reviews", neg_count)
        
        # Charts
        st.subheader("📈 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Rating Distribution")
            rating_counts = df['rating'].value_counts().sort_index()
            st.bar_chart(rating_counts)
        
        with col2:
            st.markdown("### Sentiment Distribution")
            sentiment_counts = df['sentiment'].value_counts()
            st.bar_chart(sentiment_counts)
        
        # Top Themes & Keywords
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Top Themes")
            if summary.get('top_themes'):
                for theme, count in summary['top_themes'][:5]:
                    st.write(f"**{theme}**: {count} mentions")
            else:
                st.info("No themes detected")
        
        with col2:
            st.subheader("🔑 Top Keywords")
            if summary.get('top_keywords'):
                for keyword, count in summary['top_keywords'][:10]:
                    st.write(f"**{keyword}**: {count}")
            else:
                st.info("No keywords extracted")
        
        # LLM Insights
        if summary.get('action_ideas'):
            st.subheader("💡 Action Ideas")
            for idea in summary['action_ideas'][:5]:
                st.write(f"• {idea}")
        
        if summary.get('user_quotes'):
            st.subheader("🗣️ User Quotes")
            for quote in summary['user_quotes'][:5]:
                st.write(f"> *\"{quote}\"*")
        
        # Critical Reviews
        st.subheader("⚠️ Recent Critical Reviews")
        critical = summary.get('recent_critical_reviews', [])[:5]
        if critical:
            for review in critical:
                with st.expander(f"⭐ {'★' * review['rating']} - {review['review_date']}"):
                    st.write(review.get('safe_text', review.get('review_text', '')))
        else:
            st.info("No critical reviews in this period")
        
        # Download options
        st.subheader("📥 Download Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Reviews', index=False)
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Download Excel Report",
                data=excel_buffer,
                file_name=f"reviews_{app_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"reviews_{app_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

with tab3:
    st.header("ℹ️ About")
    
    st.markdown("""
    ### 📱 App Review Scraper & Analyzer
    
    This tool helps you:
    - 📥 **Scrape reviews** from Google Play Store and Apple App Store
    - 🧠 **Analyze sentiment** using AI-powered NLP
    - 🔑 **Extract keywords** and trending topics
    - 💡 **Get insights** powered by Google's Gemini AI
    - 📧 **Send reports** via email with charts
    - 📊 **Download data** in Excel or CSV format
    
    ### 🚀 How to Use
    
    1. **Configure** your settings in the sidebar
    2. **Enter** the Google Play Store URL (Apple App Store is optional)
    3. **Click** "Start Scraping" to fetch and analyze reviews
    4. **View** results in the Results tab
    5. **Download** the data or send email reports
    
    ### 🔑 Getting API Keys
    
    **Gemini API (Free)**
    - Visit: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    - Sign in with Google account
    - Create a new API key
    - Free tier includes 60 requests per minute
    
    **Gmail App Password (For Email)**
    - Visit: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
    - Enable 2-Step Verification first
    - Generate an app password
    - Use this instead of your regular password
    
    ### 📖 Features
    
    - ✅ Multi-platform support (Google Play & Apple App Store)
    - ✅ Sentiment analysis with TextBlob
    - ✅ AI-powered insights with Gemini
    - ✅ Automated email reports with charts
    - ✅ Excel and CSV export
    - ✅ Responsive web interface
    
    ### 🔒 Privacy & Security
    
    - Your API keys are **never stored** on our servers
    - All processing happens in **your browser session**
    - Credentials are only used for the current session
    - No data is saved or shared
    
    ---
    
    💻 **Source Code**: [GitHub](https://github.com/yourusername/repo)
    
    Made with ❤️ using Streamlit
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "App Review Scraper v1.0 | Built with Streamlit 🎈"
    "</div>",
    unsafe_allow_html=True
)
