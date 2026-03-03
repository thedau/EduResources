"""URL patterns cho tính năng AI."""

from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    path('api/ai/summarize/<slug:slug>/', views.api_summarize, name='api_summarize'),
    path('api/ai/chat/<slug:slug>/', views.api_chat, name='api_chat'),
    path('api/ai/suggest-tags/', views.api_suggest_tags, name='api_suggest_tags'),
    path('api/ai/general-chat/', views.api_general_chat, name='api_general_chat'),
]
