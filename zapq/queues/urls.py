from django.urls import path
from .views import QueueList

urlpatterns = [
    path('business/create-queue/', QueueList.as_view()),
]
