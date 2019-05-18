from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import Task

from django.views import View
from django.views.generic.edit import CreateView, DeleteView

from .sprig import Line, Sprig

# def index(req):
#     posts = Post.objects.all()
#     form = PostForm()
#     context = {'posts': posts, 'form': form, }
#     return render(req, 'todo/index.html', context)
#
#
# def add(req):
#     form = PostForm(req.POST)
#     form.save(commit=True)
#     return HttpResponseRedirect(reverse('index'))
#
#
# def delete(req, id=None):
#     post = get_object_or_404(Post, pk=id)
#     post.delete()
#     return HttpResponseRedirect(reverse('index'))

class ShowTask(View):
    def show(self, req, *args, **kwargs):
        tasks = Task.objects.all()
        context = {'tasks': tasks}
        return render(req, 'todo/index.html', context)


index = ShowTask.as_view()


class CreateTask(CreateView):
    def create(self, req, *args, **kwargs):
        sprig = Sprig(req.POST['sprig'])
        for line in sprig.lines:
            task = line.to_task(Task())
            task.save(commit=True)
        return HttpResponseRedirect(reverse('index'))


add = CreateTask.as_view()


class DeleteTask(DeleteView):
    def delete(self, req, id=None):
        task = get_object_or_404(Task, pk=id)
        task.delete()
        return HttpResponseRedirect(reverse('index'))


delete = DeleteTask.as_view()
