from django.urls import path
from . import views
urlpatterns =[
    path('lists/add/', views.ListAdd.as_view()),
    path('lists/list/', views.ListFetch.as_view()),
    path('tasks/add/', views.TaskAdd.as_view()),
    path('tasks/list/', views.TaskFetch.as_view()),
    path('tasks/task/update_status/', views.TaskStatusSet.as_view()),
    path('lists/<int:list_id>/', views.ListDelete.as_view(), name='list-delete'),
    path('tasks/<int:task_id>/', views.TaskDelete.as_view(), name='task-delete'),
    path('tasks/least_time_left/', views.LeastTimeLeftTasks.as_view()),  # Add this line
]   
