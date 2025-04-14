from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tasktracker.models import Team, Task
from .serializers import TeamSerializer, TaskSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_list(request):
    """Список всех команд, где пользователь является участником"""
    teams = Team.objects.filter(teammember__user=request.user)
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_detail_api(request, id):
    """Детальная информация о команде"""
    team = Team.objects.filter(id=id, teammember__user=request.user).first()
    if not team:
        return Response({'error': 'Team not found or access denied'}, status=404)

    serializer = TeamSerializer(team)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_tasks(request, id):
    """Список задач команды"""
    team = Team.objects.filter(id=id, teammember__user=request.user).first()
    if not team:
        return Response({'error': 'Team not found or access denied'}, status=404)

    tasks = Task.objects.filter(project__team=team)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail_api(request, team_id, task_id):
    """Детальная информация о задаче"""
    task = Task.objects.filter(
        id=task_id,
        project__team__id=team_id,
        project__team__teammember__user=request.user
    ).first()

    if not task:
        return Response({'error': 'Task not found or access denied'}, status=404)

    serializer = TaskSerializer(task)
    return Response(serializer.data)