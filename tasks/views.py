from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem
from tasks.forms import TodoItemForm, TodoItemExportForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from datetime import datetime, timezone
from taggit.managers import TaggableManager
from taggit.models import Tag


@login_required
def index(request):
    return HttpResponse("Примитивный ответ из приложения tasks")


def complete_task(request, pk):
    t = TodoItem.objects.get(id=pk)
    t.is_completed = True
    t.save()
    print(pk)
    messages.success(request, "Задача завершена")
    return HttpResponse("OK")


def delete_task(request, uid):
    t = TodoItem.objects.get(id=uid)
    t.delete()
    messages.success(request, "Задача удалена")
    return redirect(request.META["HTTP_REFERER"])


class TaskCreateView(View):
    def post(self, request, *args, **kwargs):
        form = TodoItemForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            messages.success(request, "Задача создана")
            return redirect(reverse("tasks:list"))

        return render(request, "tasks/create.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = TodoItemForm()

        return render(request, "tasks/create.html", {"form": form})


def add_task(request):
    if request.method == "POST":
        desc = request.POST["description"]
        t = TodoItem(description=desc)
        t.save()
    return redirect("/tasks/list")


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = 'tasks/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_object = TodoItem.objects.get(pk=self.kwargs['pk'])
        created = task_object.created
        now = datetime.now(timezone.utc)
        days = (now - created).days
        context['days'] = days
        context['tags'] = task_object.tags.all()

        context['days_name'] = 'день' if days == 1 else 'дней'
        return context


class TaskEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(request.POST, instance=t)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            return redirect(reverse("tasks:list"))

        return render(request, "tasks/edit.html", {"form": form, "task": t})

    def get(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(instance=t)
        return render(request, "tasks/edit.html", {"form": form, "task": t})


class TaskExportView(LoginRequiredMixin, View):
    def generate_body(self, user, priorities, **kwargs):
        q = Q()
        if priorities["prio_high"]:
            q = q | Q(priority=TodoItem.PRIORITY_HIGH)
        if priorities["prio_med"]:
            q = q | Q(priority=TodoItem.PRIORITY_MEDIUM)
        if priorities["prio_low"]:
            q = q | Q(priority=TodoItem.PRIORITY_LOW)

        if 'pk' in self.kwargs:
            pk = self.kwargs['pk']
            tasks = TodoItem.objects.filter(owner=user).filter(q).all().filter(tags__in=[pk])
        else:
            tasks = TodoItem.objects.filter(owner=user).filter(q).all()
        body = "Ваши задачи и приоритеты:\n"
        for t in list(tasks):
            all_tags = t.tags.all()
            tags = ''
            if all_tags:
                tags = ', теги: '
                tags += ', '.join({tag.name for tag in all_tags})
            marker = 'x' if t.is_completed else ' '
            body += f"[{marker}] {t.description} ({t.get_priority_display()}){tags}\n"
        return body

    def post(self, request, *args, **kwargs):
        form = TodoItemExportForm(request.POST)
        if form.is_valid():
            email = request.user.email
            body = self.generate_body(request.user, form.cleaned_data)
            send_mail("Задачи", body, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Задачи были отправлены на почту %s" % email)
        else:
            messages.error(request, "Что-то пошло не так, попробуйте ещё раз")
        return redirect(reverse("tasks:list"))

    def get(self, request, *args, **kwargs):
        form = TodoItemExportForm()
        pk = None
        if 'pk' in self.kwargs:
            pk = self.kwargs['pk']
        return render(request, "tasks/export.html", {"form": form, 'tag_pk': pk})


class GroupListView(LoginRequiredMixin, View):
    model = TodoItem
    context_object_name = "tasks"

    def get_queryset(self):
        u = self.request.user
        return u.tasks.all()

    def get(self, request, *args, **kwargs):
        u = self.request.user
        low = Q(priority=TodoItem.PRIORITY_LOW)
        low = u.tasks.all().filter(low).all()
        medium = Q(priority=TodoItem.PRIORITY_MEDIUM)
        medium = u.tasks.all().filter(medium).all()
        high = Q(priority=TodoItem.PRIORITY_HIGH)
        high = u.tasks.all().filter(high).all()

        priorities = {'priorities': {
            'high': high,
            'medium': medium,
            'low': low,
        }}

        return render(request, "tasks/group.html", priorities)


class TaskListView(LoginRequiredMixin, ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    # now = int(datetime.now().hour)
    # theme = 'bg-dark' if now >= 22 or now > 6 else 'bg-white'
    # extra_context = {'theme': theme}

    def get_queryset(self, *args, **kwargs):
        u = self.request.user
        tasks = u.tasks.all()

        return tasks

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user_tasks = self.get_queryset()
        all_tags = []

        if 'tag_slug' in self.kwargs:
            tag_slug = self.kwargs['tag_slug']
            tag = get_object_or_404(Tag, slug=tag_slug)
            context['tag'] = tag
            user_tasks = user_tasks.filter(tags__in=[tag])

        user_tasks = {t: list(t.tags.all()) for t in user_tasks}

        for t in user_tasks:
            task_tags = t.tags.all()
            if task_tags:
                all_tags.extend(list(task_tags))

        context['all_tags'] = set(all_tags)
        context['user_tasks'] = user_tasks

        return context


class SuccessListView(LoginRequiredMixin, ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self, *args, **kwargs):
        u = self.request.user
        tasks = u.tasks.all()
        return tasks

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tasks = self.get_queryset()
        tasks = tasks.filter(is_completed=True)
        user_tasks = {t: list(t.tags.all()) for t in tasks}

        all_tags = []
        for t in user_tasks:
            task_tags = t.tags.all()
            if task_tags:
                all_tags.extend(list(task_tags))

        context['all_tags'] = set(all_tags)
        context['user_tasks'] = user_tasks

        return context
