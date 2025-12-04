"""
URL configuration for user app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('<uuid:public_id>/', views.user, name="get_user"),
    path('', views.users, name="get_users"),
    path('search/', views.search_users, name="search_users"),
    path('badge-status/', views.badge_status, name='badge-status'),
    path('activity/', views.user_activity, name='user-activity')
]
