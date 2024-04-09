import uuid

from celery import shared_task
from django.contrib.auth.models import User


@shared_task
def create_random_user():
    User.objects.create_user(username=uuid.uuid4())
