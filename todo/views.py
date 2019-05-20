from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import Step, Task

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
    """"""
    def get(self, req, *args, **kwargs):
        tasks = Task.objects.all()
        context = {'tasks': tasks}
        return render(req, 'todo/index.html', context)


index = ShowTask.as_view()


class CreateTask(CreateView):
    """"""
    def post(self, req, *args, **kwargs):
        try:
            existing = Task.objects.all().order_by('-pk')[0].pk
        except IndexError:
            existing = 0
        sprig = Sprig(req.POST['sprig'], existing)
        for node in sprig.ad.nodes:
            # self.step_as(node, sprig.ad.nodes).save()
            Step.objects.update_or_create(
                linker=sprig.ad.nodes[node]['linker'],
                defaults={
                    'loc': node,
                    'linker': sprig.ad.nodes[node]['linker'],
                }
            )
        for edge in sprig.ad.edges:
            # self.task_as(edge, sprig.ad.edges).save()
            Task.objects.update_or_create(
                initial_step=Step.objects.get(loc=edge[0]),
                terminal_step=Step.objects.get(loc=edge[1]),
                defaults={
                    'title': sprig.ad.edges[edge]['title'],
                    'start': sprig.ad.edges[edge]['start'],
                    'expected_time': sprig.ad.edges[edge]['expected_time'],
                    'actual_time': sprig.ad.edges[edge]['actual_time'],
                    'deadline': sprig.ad.edges[edge]['deadline'],
                    'client': sprig.ad.edges[edge]['client'],
                    'is_done': sprig.ad.edges[edge]['is_done'],
                    'note': sprig.ad.edges[edge]['note'],
                    'initial_step': Step.objects.get(loc=edge[0]),
                    'terminal_step': Step.objects.get(loc=edge[1]),
                }
            )
        return HttpResponseRedirect(reverse('index'))

    # @staticmethod
    # def step_as(node, nodes):
    #     step = Step()
    #     step.loc = node
    #     step.linker = nodes[node]['linker']
    #     return step
    #
    # @staticmethod
    # def task_as(edge, edges):
    #     task = Task()
    #     task.title = edges[edge]['title']
    #     task.start = edges[edge]['start']
    #     task.expected_time = edges[edge]['expected_time']
    #     task.actual_time = edges[edge]['actual_time']
    #     task.deadline = edges[edge]['deadline']
    #     task.client = edges[edge]['client']
    #     task.is_done = edges[edge]['is_done']
    #     task.note = edges[edge]['note']
    #     task.initial_step = Step.objects.get(loc=edge[0])
    #     task.terminal_step = Step.objects.get(loc=edge[1])
    #     return task


add = CreateTask.as_view()


class DeleteTask(DeleteView):
    """"""
    def delete(self, req, id=None):
        task = get_object_or_404(Task, pk=id)
        task.delete()
        return HttpResponseRedirect(reverse('index'))


delete = DeleteTask.as_view()
