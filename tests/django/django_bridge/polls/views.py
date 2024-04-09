# Create your views here.
from django.http.response import HttpResponse

from polls.tasks import create_random_user


def test_view(request):
    create_random_user.delay()
    return HttpResponse("Hello, world. You're at the polls index.")
