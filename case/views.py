from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.http import Http404


from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# Custom Login view
class CustomLoginView(LoginView):
    template_name = 'case/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

# Register page for user creation
class RegisterPage(FormView):
    template_name = 'case/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

# Task list view with search functionality
class task_list(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter tasks by the current logged-in user
        tasks = context['tasks'].filter(user=self.request.user)

        # Get search query from the GET request
        search_input = self.request.GET.get('search-area', '').strip().lower()

        if search_input:
            tasks = tasks.filter(title__icontains=search_input)  # Case-insensitive search
        context['tasks'] = tasks
        context['search_input'] = search_input  # Make sure you pass this context

        context['count'] = tasks.filter(complete=False).count()  # Incomplete task count

        return context

class task_detail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'case/task.html'

    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        # Check if the task belongs to the logged-in user
        if task.user != self.request.user:
            raise Http404("You do not have permission to view this task.")
        return task

# Task create view (to create a new task)
class task_create(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the current user as the task owner
        return super(task_create, self).form_valid(form)

# Task update view (to update an existing task)
class task_update(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')

    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        # Ensure the task belongs to the logged-in user before updating
        if task.user != self.request.user:
            raise Http404("You do not have permission to edit this task.")
        return task

# Task delete view (to delete a task)
class task_delete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        # Ensure the task belongs to the logged-in user before deleting
        if task.user != self.request.user:
            raise Http404("You do not have permission to delete this task.")
        return task
