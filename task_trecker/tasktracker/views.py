from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Team, TeamMember, Project, Task, Comment, Notification
from .forms import TeamForm, ProjectForm, TaskForm, CommentForm


@login_required
def dashboard(request):
    user_teams = TeamMember.objects.filter(user=request.user)
    context = {
        'user_teams': user_teams,
    }
    return render(request, 'tasktracker/dashboard.html', context)


@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user)
    projects = Project.objects.filter(team=team)
    team_members = TeamMember.objects.filter(team=team)

    context = {
        'team': team,
        'member': member,
        'projects': projects,
        'team_members': team_members,
    }
    return render(request, 'tasktracker/team_detail.html', context)


@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            TeamMember.objects.create(
                user=request.user,
                team=team,
                role='ADMIN'
            )
            messages.success(request, 'Команда успешно создана!')
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamForm()

    return render(request, 'tasktracker/create_team.html', {'form': form})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    member = get_object_or_404(TeamMember, team=project.team, user=request.user)
    tasks = Task.objects.filter(project=project)

    if request.method == 'POST':
        form = TaskForm(project.team, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = member
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project.team)

    context = {
        'project': project,
        'member': member,
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'tasktracker/project_detail.html', context)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)
    comments = Comment.objects.filter(task=task)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = member
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('task_detail', task_id=task.id)
    else:
        comment_form = CommentForm()

    context = {
        'task': task,
        'member': member,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tasktracker/task_detail.html', context)


@login_required
def update_task_status(request, task_id, new_status):
    task = get_object_or_404(Task, id=task_id)
    member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)

    if member.role in ['ADMIN', 'MANAGER'] or task.assigned_to == member:
        task.status = new_status
        if new_status == 'DONE':
            task.completed_at = timezone.now()
        task.save()
        messages.success(request, 'Статус задачи обновлен!')
    else:
        messages.error(request, 'У вас нет прав для изменения статуса этой задачи.')

    return redirect('task_detail', task_id=task.id)


@login_required
def notifications(request):
    member = TeamMember.objects.filter(user=request.user)
    notifications = Notification.objects.filter(recipient__in=member).order_by('-created_at')

    # Помечаем уведомления как прочитанные
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    context = {
        'notifications': notifications,
    }
    return render(request, 'tasktracker/notifications.html', context)


@login_required
def create_project(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user)

    if member.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, 'У вас нет прав для создания проектов')
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.team = team
            project.save()
            messages.success(request, 'Проект успешно создан!')
            return redirect('team_detail', team_id=team.id)
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'team': team,
        'member': member,
    }
    return render(request, 'tasktracker/create_project.html', context)