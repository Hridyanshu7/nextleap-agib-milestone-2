# App Store Review Scraper

An automated system to scrape, analyze, and summarize app reviews from Google Play Store and Apple App Store. The system provides sentiment analysis, keyword extraction, and automated email reports.

## Features

- 📱 **Multi-Platform Support**: Scrapes reviews from both Google Play Store and Apple App Store
- 🤖 **Automated Scraping**: Scheduled weekly scraping with customizable intervals
- 📊 **Sentiment Analysis**: Analyzes review sentiment using TextBlob NLP
- 🔑 **Keyword Extraction**: Identifies trending topics and common phrases
- 📧 **Email Reports**: Beautiful HTML email reports with key metrics
- 💾 **Database Storage**: SQLite/PostgreSQL support with deduplication
- 🎯 **Critical Review Alerts**: Highlights low-rated and negative reviews

## Installation

### Prerequisites

- Python 3.11+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nextleap-agib-milestone-2
   ```

2. **Set Python version** (if using pyenv)
   ```bash
   pyenv local 3.11.1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download TextBlob corpora**
   ```bash
   python -m textblob.download_corpora
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

Edit `config.py` or set environment variables in `.env`:



### Email Configuration

For Gmail, you need to generate an App Password:
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate an App Password at [App Passwords](https://myaccount.google.com/apppasswords)

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

## Usage

### Run Once

```bash
python main.py
```

This will:
1. Scrape reviews from configured apps
2. Analyze sentiment and extract keywords
3. Save to database
4. Generate and print summary report
5. Send email report (if configured)

### Run Scheduled

```bash
python scheduler.py
```

This will:
1. Run the scraper immediately
2. Schedule weekly runs (default: Monday 9:00 AM)
3. Log all activities to `scheduler.log`

### Customize Schedule

Edit `scheduler.py`:

```python
# Weekly on Monday at 9 AM
schedule.every().monday.at("09:00").do(job)

# Or every 5 minutes for testing
schedule.every(5).minutes.do(job)

# Or daily at 10 AM
schedule.every().day.at("10:00").do(job)
```

## Project Structure

```
nextleap-agib-milestone-2/
├── app_store_review_scraper/
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── summarizer.py          # Sentiment analysis & summarization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Database base models
│   │   └── review.py              # Review model
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── email_sender.py        # Email notification system
│   └── scrapers/
│       ├── google_play_scraper.py # Google Play scraper
│       └── app_store_scraper.py   # App Store scraper
├── config.py                      # Configuration
├── main.py                        # Main execution script
├── scheduler.py                   # Scheduling script
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
└── DEV-PLAN.md                   # Development plan
```

## Database Schema

Reviews are stored with the following fields:
- `review_id`: Unique identifier
- `source`: google_play or app_store
- `app_id`: App identifier
- `user_name`: Reviewer name
- `rating`: 1-5 stars
- `content`: Review text
- `sentiment`: positive/neutral/negative
- `sentiment_score`: -1.0 to 1.0
- `review_date`: When review was posted
- `developer_reply`: Developer response (if any)
- And more...

## Email Report

The email report includes:
- 📊 **Key Metrics**: Total reviews, average rating
- 😊 **Sentiment Distribution**: Breakdown by positive/neutral/negative
- 🔑 **Top Keywords**: Most mentioned topics
- ⚠️ **Critical Reviews**: Recent low-rated reviews with full text

## Development

### Phase 1: Setup ✅
- [x] Project structure
- [x] Dependencies
- [x] Version control

### Phase 2: Core Development ✅
- [x] Google Play scraper
- [x] App Store scraper
- [x] Database models
- [x] Sentiment analysis
- [x] Summarization engine

### Phase 3: Automation ✅
- [x] Email system
- [x] Scheduling
- [x] Logging

### Phase 4: Testing & Deployment (Next)
- [ ] Unit tests
- [ ] Docker containerization
- [ ] Cloud deployment

### Phase 5: Enhancements (Future)
- [ ] Advanced NLP (topic modeling)
- [ ] Web dashboard
- [ ] More app stores
- [ ] Real-time alerts

## Troubleshooting

### TextBlob MissingCorpusError
```bash
python -m textblob.download_corpora
```

### Email not sending
- Check SMTP credentials
- For Gmail, use App Password, not regular password
- Ensure 2-Step Verification is enabled

### No reviews fetched
- Verify app IDs are correct
- Check internet connection
- Some apps may have limited review availability

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
