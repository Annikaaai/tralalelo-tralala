"""
URL configuration for task_trecker project.

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
from django.urls import path

# urls.py
from tasktracker.views import *
from django.contrib.auth import views as auth_views

#app_name = 'tasktracker'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('team/<int:team_id>/create-project/', create_project, name='create_project'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('team/create/', create_team, name='create_team'),
    path('team/<int:team_id>/', team_detail, name='team_detail'),
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('task/<int:task_id>/update-status/<str:new_status>/', update_task_status, name='update_task_status'),
    path('notifications/', notifications, name='notifications'),
]