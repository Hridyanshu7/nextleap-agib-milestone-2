# App Review Scraper - Streamlit Deployment

## 🚀 Live Demo

Visit the live app at: **[Your App URL will be here]**

## 📋 How to Deploy on Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit web app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `nextleap-agib-milestone-2`
   - Main file path: `streamlit_app.py`
   - Click "Deploy"!

3. **Your app will be live at:**
   `https://[your-username]-nextleap-agib-milestone-2.streamlit.app`

## 🏃 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 🔑 Required Inputs

Users will need to provide:
- **Gemini API Key** (free from Google)
- **App URLs** (Google Play & Apple App Store)
- **Email credentials** (optional, for sending reports)

## ✨ Features

- 📥 Scrape reviews from Google Play & Apple App Store
- 🧠 AI-powered sentiment analysis
- 📊 Interactive visualizations
- 💡 Smart insights with Gemini AI
- 📧 Email reports with charts
- 📥 Download as Excel or CSV

## 📖 User Guide

1. Enter your Gemini API key in the sidebar
2. Configure scraping settings (days, max reviews)
3. Enter app URLs
4. Click "Start Scraping"
5. View results and download reports!

---

**Note**: All processing happens in the user's session. API keys are never stored.
