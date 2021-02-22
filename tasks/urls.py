from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.index, name="index"),
    path("list/tag/<slug:tag_slug>", views.TaskListView.as_view(), name="list_by_tag"),
    path("list/", views.TaskListView.as_view(), name="list"),
    path("success-list/", views.SuccessListView.as_view(), name="success-list"),
    path("group-list/", views.GroupListView.as_view(), name="group-list"),
    path("create/", views.TaskCreateView.as_view(), name="create"),
    path("add-task/", views.add_task, name="api-add-task"),
    path("complete/<int:pk>", views.complete_task, name="complete"),
    path("delete/<int:uid>", views.delete_task, name="delete"),
    path("details/<int:pk>", views.TaskDetailsView.as_view(), name="details"),
    path("edit/<int:pk>", views.TaskEditView.as_view(), name="edit"),
    path("export/tag/<int:pk>", views.TaskExportView.as_view(), name="export_by_tag"),
    path("export/", views.TaskExportView.as_view(), name="export"),
]
