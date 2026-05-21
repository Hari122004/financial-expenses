import os
from dotenv import load_dotenv
from utils.mail import send_welcome_email, get_smtp_settings, validate_smtp_settings

# Load environment variables
load_dotenv()

# Check if SMTP settings are configured
print("=" * 50)
print("TESTING EMAIL CONFIGURATION")
print("=" * 50)

settings = get_smtp_settings()
print("\nSMTP Settings loaded:")
print(f"  SMTP Host: {settings['host']}")
print(f"  SMTP Port: {settings['port']}")
print(f"  SMTP Username: {settings['username']}")
print(f"  SMTP From: {settings['from_email']}")
print(f"  Use TLS: {settings['use_tls']}")

try:
    validate_smtp_settings(settings)
    print("\n✓ SMTP settings validation: PASSED")
except ValueError as e:
    print(f"\n✗ SMTP settings validation FAILED:")
    print(f"  {e}")
    exit(1)

# Test sending an email
print("\nAttempting to send test email...")
try:
    send_welcome_email("test@example.com", "TestUser")
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email sending FAILED:")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {e}")
    print("\nTroubleshooting steps:")
    print("  1. Check if Gmail 2FA is enabled and app password is valid")
    print("  2. Verify SMTP_PASSWORD doesn't have extra spaces")
    print("  3. Check if 'Less secure apps' is enabled (if not using app password)")
    print("  4. Verify firewall/network allows SMTP connections to smtp.gmail.com:587")
