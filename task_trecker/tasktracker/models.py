from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

User.add_to_class('get_profile', property(
    lambda u: Profile.objects.get_or_create(user=u, defaults={'avatar_number': 1})[0]
))

from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_number = models.PositiveSmallIntegerField(default=1)

    def get_avatar_url(self):
        return f'images/avatars/default{self.avatar_number}.jpg'

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MODERATOR', 'Moderator'),
        ('DEVELOPER', 'Developer'),
        ('VIEWER', 'Viewer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='DEVELOPER')
    joined_at = models.DateTimeField(auto_now_add=True)
    def get_role_color(self):
        return self.role.lower()
    class Meta:
        unique_together = ('user', 'team')

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Планирование'),
        ('ACTIVE', 'Активный'),
        ('ON_HOLD', 'На паузе'),
        ('COMPLETED', 'Завершен'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PLANNING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return self.reverse('project_detail', args=[self.team.id, self.id])
    def get_status_color(self):
        return self.status.lower()
    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Низкий'),
        ('MEDIUM', 'Средний'),
        ('HIGH', 'Высокий'),
    ]

    STATUS_CHOICES = [
        ('TODO', 'К выполнению'),
        ('IN_PROGRESS', 'В работе'),
        ('REVIEW', 'На проверке'),
        ('DONE', 'Выполнено'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    def get_status_color(self):
        return self.status.lower()
    def get_priority_color(self):
        return self.priority.lower()
    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.user.username} on {self.task.title}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('TASK_ASSIGNED', 'Задача назначена'),
        ('TASK_UPDATED', 'Задача обновлена'),
        ('COMMENT_ADDED', 'Добавлен комментарий'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=13, choices=TYPE_CHOICES)
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)