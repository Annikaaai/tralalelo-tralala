from rest_framework import serializers
from tasktracker.models import Team, Task, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status']


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'project',
            'status',
            'priority',
            'created_at',
            'deadline',
            'completed_at'
        ]


class TeamSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'projects'
        ]