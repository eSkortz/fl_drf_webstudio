from django.urls import path, include

urlpatterns = [
    path('django_prosto/', include('feedback_service.urls')),
    path('django_prosto/', include('swagger')),
]
