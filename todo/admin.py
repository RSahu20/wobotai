from django.contrib import admin
from .models import TaskList, Task, ListAccess

@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'list', 'done', 'description']
    list_filter = ['done', 'list']

@admin.register(ListAccess)
class ListAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'list', 'role']
