from django.contrib import admin
from django.urls import path
from tasktracker.views import *
from django.contrib.auth import views as auth_views
from tasktracker.api.views import (
    team_list,
    team_detail_api,
    team_tasks,
    task_detail_api
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('update-avatar/', update_avatar, name='update_avatar'),
    path('admin/manage/', manage_admins, name='manage_admins'),
    path('admin/', admin.site.urls),
    path('', index_page, name='index'),
    path('main/', main_page, name = 'main'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout_page'),
    path('registration/', register_page, name='register'),
    path('profile/', profile_page, name='profile'),

    path('dashboard', dashboard, name='dashboard'),

    path('team/create/', create_team, name='create_team'),
    path('team/<int:team_id>/project/<int:project_id>/task/<int:task_id>/delete/',
             delete_task,
             name='delete_task'),
    # Измененные URL для команд и проектов
    path('team/<int:team_id>/', team_detail, name='team_detail'),
    path('team/<int:team_id>/update/', update_team, name='update_team'),
    path('team/<int:team_id>/add-member/', add_team_member, name='add_team_member'),
    path('team/member/<int:member_id>/change-role/', change_member_role, name='change_member_role'),
    path('team/member/<int:member_id>/remove/', remove_team_member, name='remove_team_member'),
    path('team/<int:team_id>/project/create/', create_project, name='create_project'),
    path('team/<int:team_id>/project/<int:project_id>/', project_detail, name='project_detail'),
    path('team/<int:team_id>/project/<int:project_id>/task/<int:task_id>/', task_detail, name='task_detail'),
    path('team/<int:team_id>/project/<int:project_id>/task/<int:task_id>/reassign/', reassign_task, name='reassign_task'),
    path('team/<int:team_id>/project/<int:project_id>/task/<int:task_id>/update-deadline/', update_task_deadline, name='update_task_deadline'),
    path('team/<int:team_id>/project/<int:project_id>/task/<int:task_id>/update-status/<str:new_status>/', update_task_status, name='update_task_status'),

    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),

    path('api/team/', team_list, name='api_team_list'),
    path('api/team/<int:id>/', team_detail_api, name='api_team_detail'),
    path('api/team/<int:id>/task/', team_tasks, name='api_team_tasks'),
    path('api/team/<int:team_id>/task/<int:task_id>/', task_detail_api, name='api_task_detail'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
