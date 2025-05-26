from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Graph, CustomUser
from .forms import GraphForm
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm


def is_admin(user):
    return user.user_type == 'admin'


def is_registered(user):
    return user.user_type == 'registered'


def graph_list(request):
    graphs = Graph.objects.all()
    return render(request, 'graphs/list.html', {'graphs': graphs})


@login_required
def create_graph(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            column_data = {}
            for key in request.POST:
                if key.startswith('column_name_'):
                    num = key.split('_')[-1]
                    name = request.POST.get(f'column_name_{num}')
                    value = request.POST.get(f'column_value_{num}')
                    if name and value:
                        column_data[name] = float(value)

            if column_data:
                graph = form.save(commit=False)
                graph.user = request.user
                graph.data = column_data
                graph.save()
                return redirect('graph_list')
    else:
        form = GraphForm()
    return render(request, 'graphs/create.html', {'form': form})


@login_required
def delete_graph(request, pk):
    """
    Удаление графика (только для автора или админа)
    """
    graph = get_object_or_404(Graph, pk=pk)

    if not (request.user.user_type == 'admin' or request.user == graph.user):
        raise Http404("У вас нет прав для удаления этого графика")

    if request.method == 'POST':
        graph.delete()
        messages.success(request, 'График успешно удален!')
        return redirect('graph_list')

    return render(request, 'graphs/delete.html', {'graph': graph})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('graph_list')
    else:
        form = RegisterForm()
    return render(request, 'graphs/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('graph_list')
    else:
        form = LoginForm()
    return render(request, 'graphs/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('graph_list')
