"""reflectsongs URL Configuration

"""
from django.urls import path

from reflectsongs.views import HomeView

urlpatterns = [
    path('', HomeView.as_view()),
]
