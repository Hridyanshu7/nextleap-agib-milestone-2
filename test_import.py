try:
    from app_store_review_scraper.notifications.email_sender import EmailSender
    print("Import successful!")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
except Exception as e:
    print(f"Error: {e}")
