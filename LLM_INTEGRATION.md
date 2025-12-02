# LLM-Enhanced Analysis

This project now supports **LLM-powered analysis** using Google's Gemini API for richer insights from app reviews.

## Features

When a Gemini API key is configured, the system uses AI to enhance:

### 1. **Qualitative Theme Extraction**
- **Basic**: Uses noun phrase frequency analysis
- **LLM-Enhanced**: Infers **5 broad, qualitative themes** based on user sentiment and context (e.g., "Unreliable Delivery Service" instead of just "delivery").
- **Smart Extrapolation**: Counts are estimated from a sample and scientifically extrapolated to reflect the entire dataset volume.

### 2. **Action Ideas**
- **Basic**: Generic suggestions based on keyword frequency
- **LLM-Enhanced**: Specific, actionable recommendations tailored to the actual issues mentioned in reviews

### 3. **User Quotes**
- **Basic**: Random sampling
- **LLM-Enhanced**: Intelligently selects the most representative quotes that cover different aspects of user experience

### 4. **Visual Insights** (New!)
- **Sentiment Distribution Chart**: A beautiful area chart (KDE plot) in the email report showing the continuous distribution of sentiment scores, helping you visualize the polarity of user feedback at a glance.

## Setup

### 1. Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 2. Configure the API Key

Add to your `.env` file:

```env
GEMINI_API_KEY=your-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `google-generativeai`, `matplotlib`, and `seaborn`.

## How It Works

The `ReviewAnalyzer` class automatically detects if a Gemini API key is available:

- **With API Key**: Uses LLM-powered analysis for themes, quotes, and action ideas
- **Without API Key**: Falls back to basic TextBlob-based analysis

### Robustness & Fallback

- **JSON Parsing**: The system now robustly handles LLM responses, stripping markdown and extra text to prevent parsing errors.
- **Fallback**: If the LLM call fails (network issues, API limits), the system automatically falls back to the basic analysis method.

## Cost Considerations

- Gemini API has a **free tier** with generous limits
- The system samples reviews (max 100 for themes, 50 for actions/quotes) to minimize API calls
- Each scraper run makes approximately 3 API calls
- Review text is truncated to 200 characters per review to stay within token limits

## Privacy

- All PII (emails, phone numbers) is scrubbed before sending to the LLM
- Only review text content is sent to the API
- No user names or identifiable information is included

## Example Output Comparison

### Basic Analysis
**Themes**: "customer service", "delivery time", "app interface"
**Action**: "Investigate issues related to 'customer service'"

### LLM-Enhanced Analysis
**Themes**: "Payment Processing Failures", "Late Delivery Issues", "App Crashes on Checkout", "Rude Support Staff", "Hidden Charges"
**Action**: "Implement retry logic for failed payment transactions and add user-friendly error messages"

## Disabling LLM Analysis

Simply remove or comment out the `GEMINI_API_KEY` from your `.env` file. The system will automatically use basic analysis.

## Troubleshooting

### "Gemini API key provided but google-generativeai not installed"
Run: `pip install google-generativeai`

### "LLM theme extraction failed"
Check your API key is valid and you haven't exceeded rate limits. The system will fall back to basic analysis automatically.

### API Rate Limits
If you're processing many apps, consider adding a delay between runs or using the basic analysis for some apps.
