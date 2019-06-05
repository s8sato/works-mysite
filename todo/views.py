from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import Step, Task

from django.views import View
from django.views.generic.edit import CreateView, DeleteView

from .sprig import Line, Sprig
import datetime


class ShowTask(View):
    """"""
    def get(self, req, *args, **kwargs):
        tasks = Task.objects.all()
        context = {
            'taskss': {
                'tasks': tasks
            }
        }
        return render(req, 'todo/index.html', context)

    def post(self, req, *args, **kwargs):
        return HttpResponseRedirect(reverse('index'))


index = ShowTask.as_view()


class CreateTask(CreateView):
    """"""
    def post(self, req, *args, **kwargs):
        # 入力テキストを有向グラフ構造をもったSprigインスタンスに変換する
        sprig = Sprig(req.POST['sprig'])

        # sprigのnodeを調べてstepを登録
        node2step = {}
        for node in sprig.ad.nodes:
            # 既存のnodeを指すか調べ、そうでなければ新しく作る
            try:
                step = Step.objects.get(pk=int(sprig.ad.nodes[node]['linker']))
            except Step.DoesNotExist:
                step = Step()
                step.save()
            except ValueError:
                step = Step()
                step.save()
            # node番号（一時的）とstep.pk（永続的）との対応をとる
            node2step[node] = step.pk

        # sprigのedgeを調べてtaskを登録
        is_new_task = False
        for edge in sprig.ad.edges:
            # 既存のedgeを指すか調べ、そうでなければ新しく作る
            try:
                task = Task.objects.get(
                    initial_step=Step.objects.get(pk=node2step[edge[0]]),
                    terminal_step=Step.objects.get(pk=node2step[edge[1]])
                )
            except Task.DoesNotExist:
                task = Task()
                is_new_task = True

            # 値を更新、または新しく設定
            task.title = sprig.ad.edges[edge]['title']
            task.start = sprig.ad.edges[edge]['start']
            task.expected_time = sprig.ad.edges[edge]['expected_time']
            task.actual_time = sprig.ad.edges[edge]['actual_time']
            task.deadline = sprig.ad.edges[edge]['deadline']
            task.client = sprig.ad.edges[edge]['client']
            task.is_done = sprig.ad.edges[edge]['is_done']
            task.note = sprig.ad.edges[edge]['note']
            task.initial_step = Step.objects.get(pk=node2step[edge[0]])
            task.terminal_step = Step.objects.get(pk=node2step[edge[1]])

            if is_new_task:
                task.save()
                is_new_task = False

        return HttpResponseRedirect(reverse('index'))


add = CreateTask.as_view()


class DeleteTask(DeleteView):
    """"""
    def delete(self, req, id=None):
        task = get_object_or_404(Task, pk=id)
        task.delete()
        return HttpResponseRedirect(reverse('index'))


delete = DeleteTask.as_view()


class ShowTaskAround1(View):
    """"""
    def get(self, req, id=None):
        me = Task.objects.filter(pk=id).all()
        _me = me.get()
        initial = Step.objects.get(pk=_me.initial_step.pk)
        terminal = Step.objects.get(pk=_me.terminal_step.pk)
        in_tasks = Task.objects.filter(terminal_step=initial).all()
        out_tasks = Task.objects.filter(initial_step=terminal).all()

        context = {
            'taskss': {
                'out_tasks': out_tasks,
                'me': me,
                'in_tasks': in_tasks,
            }
        }
        return render(req, 'todo/index.html', context)

    def post(self, req, id=None):
        return HttpResponseRedirect(reverse('show_around_1', args=[id]))


show_around_1 = ShowTaskAround1.as_view()


class ShowTaskBuds(View):
    """"""
    def get(self, req, *args, **kwargs):
        tasks = Task.objects.filter(is_done=False).all()
        # bus(初動タスク)であるとは、始点がどんなタスクの終点でもないこと
        terminal_steps = [task.terminal_step for task in tasks]
        buds = [_ for _ in tasks if _.initial_step not in terminal_steps]

        context = {
            'taskss': {
                'tasks': buds
            }
        }
        return render(req, 'todo/index.html', context)

    def post(self, req, *args, **kwargs):
        return HttpResponseRedirect(reverse('show_buds'))


show_buds = ShowTaskBuds.as_view()


class ShowTaskTrunk(View):
    """"""
    def get(self, req, *args, **kwargs):
        tasks = Task.objects.filter(is_done=False).all()
        # trunk(幹、最終タスク)であるとは、終点がどんなタスクの始点でもないこと
        initial_steps = [task.initial_step for task in tasks]
        trunk = [_ for _ in tasks if _.terminal_step not in initial_steps]

        context = {
            'taskss': {
                'tasks': trunk
            }
        }
        return render(req, 'todo/index.html', context)

    def post(self, req, *args, **kwargs):
        return HttpResponseRedirect(reverse('show_trunk'))


show_trunk = ShowTaskTrunk.as_view()