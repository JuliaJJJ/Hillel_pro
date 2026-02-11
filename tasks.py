import time

try:
    from celery_app import celery_app
except ImportError:
    celery_app = None


if celery_app:
    @celery_app.task(name="tasks.send_confirmation_email")
    def send_confirmation_email(email: str):
        print(f"[EMAIL] Sending confirmation email to {email}")
        time.sleep(3)
        print(f"[EMAIL] Confirmation email sent to {email}")



