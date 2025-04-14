from django import forms
from .models import Team, Project, Task, Comment, TeamMember


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TaskForm(forms.ModelForm):
    def __init__(self, team, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = TeamMember.objects.filter(team=team)

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Добавьте комментарий...'}),
        }



class RegisterUserForm(forms.Form):
    username = forms.CharField(
        max_length=32,
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"})
    )
    password = forms.CharField(
        max_length=32,
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"})
    )



class AddTeamMemberForm(forms.Form):
    user_id = forms.IntegerField()
    role = forms.ChoiceField(choices=TeamMember.ROLE_CHOICES)