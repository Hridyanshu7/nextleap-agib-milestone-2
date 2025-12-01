# Email Testing Setup Guide

## Quick Start

To test the email functionality, you need to configure your email credentials.

### Step 1: Create .env file

Create a file named `.env` in the project root with the following content:

```env
# Scraping Configuration
SCRAPE_DAYS=30
MAX_REVIEWS=10

# Database
DATABASE_URL=sqlite:///reviews.db

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

### Step 2: Get Gmail App Password (if using Gmail)

1. Go to your Google Account: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other (Custom name)** → Enter "App Review Scraper"
6. Click **Generate**
7. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
8. Paste it in your `.env` file as `SMTP_PASSWORD` (remove spaces)

### Step 3: Update .env with your details

Replace the following in your `.env` file:
- `your-email@gmail.com` → Your Gmail address
- `your-app-password-here` → The 16-character app password (no spaces)
- `recipient1@example.com` → Email address(es) to receive reports

### Step 4: Run the test

```bash
python test_email.py
```

This will send a test email with sample review data.

## Alternative Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

### Custom SMTP Server
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
```

## Troubleshooting

### "Authentication failed"
- Make sure you're using an **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled

### "Connection refused"
- Check SMTP_SERVER and SMTP_PORT are correct
- Ensure your firewall allows outbound connections on port 587

### "No recipient emails configured"
- Make sure RECIPIENT_EMAILS is set in .env
- Multiple emails should be comma-separated

## Testing Without Email

If you want to test the scraper without email, simply leave the email fields empty in `.env`:

```env
SMTP_USER=
SMTP_PASSWORD=
RECIPIENT_EMAILS=
```

The scraper will run and display results in the console, but skip email sending.
