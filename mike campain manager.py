from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class Campaign(models.Model):
    subject = models.CharField(max_length=255)
    preview_text = models.CharField(max_length=255)
    article_url = models.URLField()
    html_content = models.TextField()
    plain_text_content = models.TextField()
    published_date = models.DateTimeField()

from django.contrib import admin
from .models import Subscriber, Campaign

admin.site.register(Subscriber)
admin.site.register(Campaign)

python
Copy code
from django.http import JsonResponse
from .models import Subscriber

def unsubscribe(request, email):
    try:
        subscriber = Subscriber.objects.get(email=email)
        subscriber.is_active = False
        subscriber.save()
        return JsonResponse({'status':'success'}, status=200)
    except Subscriber.DoesNotExist:
        return JsonResponse({'status':'not found'}, status=404)
And in your urls.py:

python
Copy code
from django.urls import path
from .views import unsubscribe

urlpatterns = [
    path('unsubscribe/<str:email>', unsubscribe, name='unsubscribe'),
]

python
Copy code
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import Campaign, Subscriber

def send_campaign(request, campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        active_subscribers = Subscriber.objects.filter(is_active=True)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = campaign.subject
        msg.attach(MIMEText(campaign.plain_text_content, 'plain'))
        msg.attach(MIMEText(campaign.html_content, 'html'))

        smtp_server = smtplib.SMTP('smtp.mailgun.org')
        smtp_server.login('your_username', 'your_password')

        for subscriber in active_subscribers:
            msg['To'] = subscriber.email
            smtp_server.sendmail('from_email', subscriber.email, msg.as_string())

        smtp_server.quit()

        return JsonResponse({'status':'success'}, status=200)
    except Campaign.DoesNotExist:
        return JsonResponse({'status':'not found'}, status=404)

def send_email(smtp_server, msg, subscriber):
    msg['To'] = subscriber.email
    smtp_server.sendmail('from_email', subscriber.email, msg.as_string())

for subscriber in active_subscribers:
    threading.Thread(target=send_email, args=(smtp_server, msg, subscriber)).start()