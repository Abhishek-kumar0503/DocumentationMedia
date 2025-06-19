from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ai-chat/<str:tool_name>/', views.ai_chat, name='ai_chat'),
    path('ai-chat/', views.ai_chat, name='ai_chat_default'),
    path('chat-api/', views.chat_api, name='chat_api'),
    path('docs/<int:doc_id>/', views.docs, name='docs'),
    path('copy_doc_text/', views.copy_doc_text, name='copy_doc_text'),
    path('copy_ai_summary/', views.copy_ai_summary, name='copy_ai_summary'),
    path('debug_db/', views.debug_db, name='debug_db'),
    # API endpoints for shared chats
    path('api/shared-chats/', views.create_shared_chat, name='create_shared_chat'),
    path('api/shared-chats/<str:chat_id>/', views.get_shared_chat, name='get_shared_chat'),
]
