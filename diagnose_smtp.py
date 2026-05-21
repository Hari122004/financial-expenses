import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DETAILED SMTP CONNECTION TEST")
print("=" * 60)

# Get SMTP settings
smtp_host = os.getenv("SMTP_HOST", "")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
smtp_username = os.getenv("SMTP_USERNAME", "")
smtp_password = os.getenv("SMTP_PASSWORD", "")
smtp_from = os.getenv("SMTP_FROM", smtp_username)
smtp_use_tls = os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "yes", "y")

print(f"\nConfiguration:")
print(f"  Host: {smtp_host}")
print(f"  Port: {smtp_port}")
print(f"  Username: {smtp_username}")
print(f"  From Email: {smtp_from}")
print(f"  Use TLS: {smtp_use_tls}")
print(f"  Password length: {len(smtp_password)} characters")

# Test connection
print("\n" + "=" * 60)
print("STEP 1: Testing SMTP Connection")
print("=" * 60)

try:
    print(f"Connecting to {smtp_host}:{smtp_port}...")
    smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    print("✓ Connected successfully")
    
    print("\nStarting TLS...")
    smtp.starttls()
    print("✓ TLS started")
    
    print(f"\nLogging in with {smtp_username}...")
    smtp.login(smtp_username, smtp_password)
    print("✓ Login successful")
    
    print("\n✓ SMTP connection test PASSED")
    smtp.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"✗ Authentication failed: {e}")
    print("\nSolutions:")
    print("  1. Check if Gmail 2FA is enabled")
    print("  2. Generate a new App Password at myaccount.google.com/apppasswords")
    print("  3. Make sure SMTP_PASSWORD has no extra spaces")
    
except smtplib.SMTPException as e:
    print(f"✗ SMTP error: {e}")
    print(f"\nError code: {e.smtp_code}")
    print(f"Error message: {e.smtp_error}")
    
except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}: {e}")

# Test sending email
print("\n" + "=" * 60)
print("STEP 2: Testing Email Send")
print("=" * 60)

test_recipient = input("\nEnter a real email to test sending (e.g., your email): ").strip()

if test_recipient:
    try:
        from email.message import EmailMessage
        
        smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        
        message = EmailMessage()
        message["Subject"] = "Test Email from Expense Tracker"
        message["From"] = smtp_from
        message["To"] = test_recipient
        message.set_content("This is a test email from your Expense Tracker application.")
        
        print(f"\nSending test email to {test_recipient}...")
        smtp.send_message(message)
        print("✓ Email sent successfully!")
        print(f"\nCheck {test_recipient} for the test email (may take a few seconds)")
        
        smtp.quit()
        
    except Exception as e:
        print(f"✗ Failed to send email: {type(e).__name__}")
        print(f"  {e}")
