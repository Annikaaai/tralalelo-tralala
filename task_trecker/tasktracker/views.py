from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Team, TeamMember, Project, Task, Comment, Notification
from .forms import TeamForm, ProjectForm, TaskForm, CommentForm, RegisterUserForm, AddTeamMemberForm
from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

@login_required
def dashboard(request):
    if(request.user.is_staff):
        user_teams = TeamMember.objects.all()
    else:
        user_teams = TeamMember.objects.filter(user=request.user)

    context = {
        'user_teams': user_teams,
    }
    return render(request, 'tasktracker/dashboard.html', context)

def index_page(request):
    context={}
    return render(request, 'tasktracker/index.html', context)

def main_page(request):
    context = {}
    return render(request, 'tasktracker/main.html', context)


@login_required
def profile_page(request):
    try:
        # Получаем всех членов команд для пользователя
        members = TeamMember.objects.filter(user=request.user)

        # Получаем все задачи для всех команд пользователя
        tasks = Task.objects.filter(assigned_to__in=members)

        # Получаем все проекты для всех команд пользователя
        projects = Project.objects.filter(team__teammember__user=request.user).distinct()

    except TeamMember.DoesNotExist:
        members = None
        tasks = []
        projects = []

    avatar_number = str(request.user.profile.avatar_number) if hasattr(request.user, 'profile') else '1'

    context = {
        'avatar_number': avatar_number,
        'user': request.user,
        'tasks': tasks,
        'projects': projects,
        'members': members,  # Теперь передаем всех членов команд
    }
    return render(request, 'tasktracker/profile.html', context)


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
def project_detail(request, team_id, project_id):
    project = get_object_or_404(Project, id=project_id, team_id=team_id)
    if (request.user.is_staff):
        try:
            member = get_object_or_404(TeamMember, team=team_id, user=request.user)
        except:
            member = None
    else:
        member = get_object_or_404(TeamMember, team=team_id, user=request.user)
    tasks = Task.objects.filter(project=project)

    if request.method == 'POST':
        form = TaskForm(project.team, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = member
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('project_detail', team_id=team_id, project_id=project.id)
    else:
        form = TaskForm(project.team)

    context = {
        'project': project,
        'member': member,
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'tasktracker/project_detail.html', context)


def delete_task(request, team_id, project_id, task_id):
    task = get_object_or_404(Task, id=task_id, project_id=project_id, project__team_id=team_id)
    member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)

    # Проверяем права на удаление (админы, менеджеры или создатель задачи)
    if member.role in ['ADMIN', 'MANAGER'] or task.created_by == member:
        task.delete()
        messages.success(request, 'Задача успешно удалена!')
        return redirect('project_detail', team_id=team_id, project_id=project_id)
    else:
        messages.error(request, 'У вас нет прав для удаления этой задачи')
        return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task_id)


@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if (request.user.is_staff):
        try:
            member = get_object_or_404(TeamMember, team=team, user=request.user)
        except:
            member = None
    else:
        member = get_object_or_404(TeamMember, team=team, user=request.user)

    # member = get_object_or_404(TeamMember, team=team, user=request.user)
    projects = Project.objects.filter(team=team)
    team_members = TeamMember.objects.filter(team=team)

    # Получаем пользователей, которые еще не в команде
    current_member_ids = team_members.values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=current_member_ids).exclude(id=request.user.id)
    roles = [
        ('MODERATOR', 'Moderator'),
        ('DEVELOPER', 'Developer'),
        ('VIEWER', 'Viewer'),
    ]
    context = {
        'team': team,
        'member': member,
        'projects': projects,
        'team_members': team_members,
        'available_users': available_users,
        'ROLES': roles
    }
    return render(request, 'tasktracker/team_detail.html', context)

@login_required
def task_detail(request, team_id, project_id, task_id):
    task = get_object_or_404(Task, id=task_id, project_id=project_id, project__team_id=team_id)
    if (request.user.is_staff):
        try:
            member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)
        except:
            member = None
    else:
        member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)

    comments = Comment.objects.filter(task=task)

    if request.method == 'POST':
        # Обработка добавления комментария
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = member
                comment.save()
                messages.success(request, 'Комментарий добавлен!')
                return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)

        # Обработка редактирования комментария
        elif 'edit_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, task=task, author=member)
            comment.text = request.POST.get('text')
            comment.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)

        # Обработка удаления комментария
        elif 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, task=task, author=member)
            comment.delete()
            messages.success(request, 'Комментарий удален!')
            return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)

        # Обработка редактирования задачи
        elif 'edit_task' in request.POST:
            if member.role in ['ADMIN', 'MANAGER'] or task.created_by == member:
                task.title = request.POST.get('title')
                task.description = request.POST.get('description')
                task.deadline = request.POST.get('deadline')
                task.status = request.POST.get('status')
                task.priority = request.POST.get('priority')
                task.save()
                messages.success(request, 'Задача обновлена!')
                return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)
            else:
                messages.error(request, 'У вас нет прав для редактирования этой задачи')

    else:
        # GET-запрос - создаем пустую форму
        comment_form = CommentForm()

    context = {
        'task': task,
        'member': member,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tasktracker/task_detail.html', context)





@login_required
def update_task_status(request, team_id, project_id, task_id, new_status):
    task = get_object_or_404(Task, id=task_id, project_id=project_id, project__team_id=team_id)

    member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)

    if member.role in ['ADMIN', 'MODERATOR'] or task.assigned_to == member:
        task.status = new_status
        if new_status == 'DONE':
            task.completed_at = datetime.now()
        task.save()
        messages.success(request, 'Статус задачи обновлен!')
    else:
        messages.error(request, 'У вас нет прав для изменения статуса этой задачи.')

    return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)


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

    if member.role not in ['ADMIN', 'MODERATOR']:
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


@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tasktracker/notifications.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1
    })


@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'Все уведомления помечены как прочитанные')
    return redirect('notifications')


@login_required
def delete_task(request, team_id, project_id, task_id):
    # Получаем задачу с проверкой принадлежности к проекту и команде
    task = get_object_or_404(
        Task,
        id=task_id,
        project_id=project_id,
        project__team_id=team_id
    )

    # Проверяем права пользователя (админ, менеджер или создатель задачи)
    member = request.user.teammember_set.filter(team_id=team_id).first()
    if not member or (member.role not in ['ADMIN', 'MODERATOR'] and task.created_by != member):
        messages.error(request, 'У вас нет прав для удаления этой задачи')
        return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task_id)

    if request.method == 'POST':
        # Сохраняем информацию для сообщения
        project_id = task.project.id
        team_id = task.project.team.id
        task_title = task.title

        # Удаляем задачу
        task.delete()

        messages.success(request, f'Задача "{task_title}" успешно удалена')
        return redirect('project_detail', team_id=team_id, project_id=project_id)

    # Если метод не POST, перенаправляем на страницу задачи
    return redirect('project_detail', team_id=team_id, project_id=project_id)




def register_page(request):
    context = {}
    context["form"] = RegisterUserForm()
    context["errors"] = []
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            context["form"] = form
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user_check = User.objects.filter(username=username)
            if user_check:
                context["errors"].append("Этот логин уже занят...")
            else:
                user = User(username=username)
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect("/")
    return render(request, 'registration/registration.html', context)

def login_page(request):
    context = {}
    context["form"] = RegisterUserForm()
    context["errors"] = []
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            context["form"] = form
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/profile")
            context["errors"].append("Неверные данные...")

    return render(request, 'registration/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('/login')


@login_required
def add_team_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, team=team, user=request.user)

    # Проверка прав (только админы могут добавлять участников)
    if member.role not in ['ADMIN', 'MODERATOR']:
        messages.error(request, 'У вас нет прав для добавления участников')
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        form = AddTeamMemberForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            role = form.cleaned_data['role']
            # остальная логика
        # user_id = request.POST.get('user_id')
        # role = request.POST.get('role')

            try:
                user_to_add = User.objects.get(id=user_id)
                if user_to_add == request.user:
                    messages.error(request, 'Вы не можете добавить себя в команду')
                    return redirect('team_detail', team_id=team.id)
                # Проверяем, что пользователь еще не в команде
                if TeamMember.objects.filter(team=team, user=user_to_add).exists():
                    messages.error(request, 'Этот пользователь уже в команде')
                else:
                    TeamMember.objects.create(
                        user=user_to_add,
                        team=team,
                        role=role
                    )
                    messages.success(request, 'Пользователь успешно добавлен в команду')

                    # Создаем уведомление для нового участника
                    new_member = TeamMember.objects.get(team=team, user=user_to_add)
                    Notification.objects.create(
                        recipient=user_to_add,  # или request.user
                        team=team,  # если нужно
                        message=f'Вас добавили в команду "{team.name}" с ролью {new_member.get_role_display()}',
                        notification_type='TASK_ASSIGNED'
                    )

            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден')

        return redirect('team_detail', team_id=team.id)

    # Если метод не POST, перенаправляем на страницу команды
    return redirect('team_detail', team_id=team.id)


@login_required
@login_required
def change_member_role(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    team = team_member.team

    if request.method == 'POST':
        new_role = request.POST.get('new_role')

        if new_role in dict(TeamMember.ROLE_CHOICES):
            # Сначала сохраняем старое значение для сообщения
            old_role_display = team_member.get_role_display()
            team_member.role = new_role
            team_member.save()

            # Создаем уведомление после сохранения
            Notification.objects.create(
                recipient=team_member.user,
                team=team,
                message=f'Ваша роль в команде "{team.name}" изменена с {old_role_display} на {team_member.get_role_display()}',
                notification_type='TASK_UPDATED'
            )

            messages.success(request, 'Роль участника успешно изменена')
        else:
            messages.error(request, 'Некорректная роль')

    return redirect('team_detail', team_id=team.id)


@login_required
def remove_team_member(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    team = team_member.team
    user_to_remove = team_member.user

    # Проверка прав
    current_member = get_object_or_404(TeamMember, team=team, user=request.user)
    if current_member.role != 'ADMIN':
        messages.error(request, 'У вас нет прав для удаления участников')
        return redirect('team_detail', team_id=team.id)

    if user_to_remove == request.user:
        messages.error(request, 'Вы не можете удалить себя из команды')
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        # Создаем уведомление (теперь оно привязано к User, а не к TeamMember)
        Notification.objects.create(
            recipient=user_to_remove,
            team=team,
            message=f'Вас удалили из команды "{team.name}"',
            notification_type='TASK_UPDATED'
        )

        # Удаляем участника (уведомления останутся, так как они привязаны к User)
        team_member.delete()
        messages.success(request, f'Пользователь {user_to_remove.username} удален из команды')

    return redirect('team_detail', team_id=team.id)


@login_required
def update_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Проверяем, что пользователь - админ команды
    try:
        member = TeamMember.objects.get(team=team, user=request.user)
        if member.role != 'ADMIN':
            messages.error(request, 'Только администратор может редактировать команду')
            return redirect('team_detail', team_id=team.id)
    except TeamMember.DoesNotExist:
        messages.error(request, 'Вы не состоите в этой команде')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            updated_team = form.save()

            # Создаем уведомление для всех участников команды
            team_members = TeamMember.objects.filter(team=team).exclude(user=request.user)
            for tm in team_members:
                Notification.objects.create(
                    recipient=tm.user,
                    team=team,
                    message=f'Администратор обновил информацию о команде "{updated_team.name}"',
                    notification_type='TASK_UPDATED'
                )

            messages.success(request, 'Информация о команде успешно обновлена')
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamForm(instance=team)

    context = {
        'form': form,
        'team': team,
        'member': member,
    }
    return render(request, 'tasktracker/update_team.html', context)


@login_required
def reassign_task(request, team_id, project_id, task_id):
    task = get_object_or_404(Task, id=task_id, project_id=project_id, project__team_id=team_id)
    project = task.project
    team = project.team

    # Проверка прав доступа
    member = get_object_or_404(TeamMember, team=team, user=request.user)
    if member.role not in ['ADMIN', 'MODERATOR'] and task.assigned_to != member:
        messages.error(request, 'У вас нет прав для переназначения этой задачи')
        return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task_id)

    if request.method == 'POST':
        assignee_id = request.POST.get('assignee')

        if assignee_id:
            try:
                new_assignee = TeamMember.objects.get(id=assignee_id, team=team)

                # Сохраняем предыдущего исполнителя для уведомления
                old_assignee = task.assigned_to
                task.assigned_to = new_assignee
                task.save()

                # Уведомление новому исполнителю
                Notification.objects.create(
                    recipient=new_assignee.user,
                    team=team,
                    message=f'Вам назначена задача "{task.title}" в проекте "{project.name}"',
                    notification_type='TASK_ASSIGNED',
                    related_task=task
                )

                # Уведомление старому исполнителю (если был)
                if old_assignee and old_assignee != new_assignee:
                    Notification.objects.create(
                        recipient=old_assignee.user,
                        team=team,
                        message=f'Задача "{task.title}" переназначена другому исполнителю',
                        notification_type='TASK_UPDATED',
                        related_task=task
                    )

                messages.success(request, 'Исполнитель задачи успешно обновлен')
            except TeamMember.DoesNotExist:
                messages.error(request, 'Выбранный участник не найден в команде')
        else:
            # Снятие назначения
            if task.assigned_to:
                old_assignee = task.assigned_to
                task.assigned_to = None
                task.save()

                Notification.objects.create(
                    recipient=old_assignee.user,
                    team=team,
                    message=f'С вас снята задача "{task.title}"',
                    notification_type='TASK_UPDATED',
                    related_task=task
                )
                messages.success(request, 'Исполнитель задачи снят')

    return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task_id)


@login_required
def update_task_deadline(request, team_id, project_id, task_id):
    task = get_object_or_404(Task, id=task_id, project_id=project_id, project__team_id=team_id)
    member = get_object_or_404(TeamMember, team=task.project.team, user=request.user)

    # Проверка прав (только ADMIN и MODERATOR)
    if member.role not in ['ADMIN', 'MODERATOR']:
        messages.error(request, 'У вас нет прав для изменения дедлайна')
        return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)

    if request.method == 'POST':
        deadline_str = request.POST.get('deadline')
        try:
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                task.deadline = deadline
            else:
                task.deadline = None
            task.save()
            messages.success(request, 'Дедлайн задачи обновлен')
        except ValueError:
            messages.error(request, 'Некорректный формат даты')

    return redirect('task_detail', team_id=team_id, project_id=project_id, task_id=task.id)



def staff_required(view_func):
    """
    Декоратор для проверки, что пользователь - staff (is_staff=True)
    """
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/'  # или ваш URL для входа
    )(view_func)

@staff_required
def manage_admins(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = User.objects.get(id=user_id)

        if action == 'make_admin':
            user.is_staff = True
            user.save()
        elif action == 'remove_admin':
            user.is_staff = False
            user.save()

    users = User.objects.all()
    return render(request, 'admin/manage_admins.html', {'users': users})



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def update_avatar(request):
    if request.method == 'POST':
        avatar_number = request.POST.get('avatar_number')
        if avatar_number and avatar_number.isdigit():
            profile = request.user.get_profile
            profile.avatar_number = int(avatar_number)
            profile.save()
    return redirect('profile')