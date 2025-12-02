# Changelog

All notable changes to the App Store Review Scraper project will be documented in this file.

## [Unreleased] - 2025-12-02

### Added
- **LLM Integration**: Added support for Google Gemini API (`gemini-2.5-flash`) to provide richer insights.
  - **Qualitative Themes**: Extracts 5 inferred themes (e.g., "Unreliable Delivery") instead of simple keywords.
  - **Actionable Insights**: Generates specific, implementable recommendations from negative reviews.
  - **Smart Quotes**: Selects representative user quotes covering diverse feedback.
- **Visualizations**: Added **Sentiment Distribution Chart** (KDE plot) to email reports using `matplotlib` and `seaborn`.
- **Interactive Scraping**: `main.py` now prompts for a Google Play URL and automatically detects language/country.
- **Cross-Platform Support**: Automatically looks up and scrapes the corresponding Apple App Store app if found.
- **Robustness**:
  - Implemented robust JSON extraction for LLM responses to handle markdown formatting.
  - Added smart extrapolation for theme counts to reflect full dataset volume.
  - Added timeouts and better error logging for SMTP email sending.

### Changed
- **App Name Detection**: Now fetches the actual app name from Google Play Store instead of using the package name.
- **Email Template**: Updated HTML template to include the new charts, 5 themes, and cleaner layout.
- **Dependencies**: Added `google-generativeai`, `matplotlib`, and `seaborn` to `requirements.txt`.
- **Model Update**: Switched from deprecated `gemini-pro` to `gemini-2.5-flash` for better performance.

### Fixed
- **JSON Parsing Error**: Fixed `Expecting value: line 1 column 1` error by stripping markdown code blocks from LLM responses.
- **Theme Counts**: Fixed low theme counts by extrapolating sample data to the full dataset size.
- **Email Sending**: Fixed potential hanging issues by adding SMTP timeouts.

## [0.1.0] - Initial Release

### Added
- Basic scraping for Google Play Store.
- Sentiment analysis using TextBlob.
- SQLite database storage.
- Basic email reporting with summary metrics.
