# 🚀 Quick Start Guide - Streamlit Web App

## Run Locally (Recommended for Testing)

```bash
streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud (Free Public Link)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Streamlit web app"
git push origin main
```

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure:
   - **Repository**: `your-username/nextleap-agib-milestone-2`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **"Deploy"**!

### Step 3: Get Your Public Link
Your app will be live at:
```
https://[your-username]-nextleap-agib-milestone-2.streamlit.app
```

**That's it!** Share this link with anyone. 🎉

## 📱 Using the Web App

### Required Inputs (provided by users on UI):
1. **Gemini API Key** 🔑
   - Free from: https://makersuite.google.com/app/apikey
   - 60 requests/minute on free tier

2. **App URLs** 📱
   - Google Play Store URL (required)
   - Apple App Store URL (optional)

3. **Scraping Settings** ⚙️
   - Days to scrape (1-90)
   - Maximum reviews (10-5000)

4. **Email Settings** 📧 (Optional)
   - SMTP Server, Port
   - Email Address & App Password
   - Recipient emails

### Features:
- ✅ Real-time scraping & analysis
- ✅ Interactive charts & visualizations
- ✅ AI-powered insights (Gemini)
- ✅ Download Excel/CSV reports
- ✅ Optional email reports with charts

## 🔒 Security

- API keys are **not stored** anywhere
- All processing in user's browser session
- Session data cleared on refresh
- No data persistence

## 💡 Tips

- Test locally first with `streamlit run streamlit_app.py`
- Use the default Groww app URLs for quick testing
- Gemini API is optional but recommended for insights
- Email feature can be skipped if not needed

---

**Need help?** Check the "About" tab in the web app for detailed instructions!
