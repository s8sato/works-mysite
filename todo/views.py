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
        # tasks = Task.objects.filter(is_done=False).all()
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

        node2step = {}
        new_edges = list(sprig.ad.edges)
        # 既存のtaskに相当するedgeを調べ上げ
        for edge in sprig.ad.edges:
            try:
                task = Task.objects.get(pk=sprig.ad.edges[edge]['pk'])
                # nodeとstepの対応をとる
                node2step[edge[0]] = task.initial_step.pk
                node2step[edge[1]] = task.terminal_step.pk
                # 新規にtaskとして登録する候補から外す
                new_edges.remove(edge)
            except Task.DoesNotExist:
                pass

        # 既存のtaskに相当しないedgeについて
        for edge in new_edges:
            # 両端のnodeに対応するstepを用意
            try:
                initial_step = Step.objects.get(pk=node2step[edge[0]])
            except Step.DoesNotExist:
                initial_step = Step()
            except KeyError:
                initial_step = Step()
            finally:
                initial_step.save()
                node2step[edge[0]] = initial_step.pk
            try:
                terminal_step = Step.objects.get(pk=node2step[edge[1]])
            except Step.DoesNotExist:
                terminal_step = Step()
            except KeyError:
                terminal_step = Step()
            finally:
                terminal_step.save()
                node2step[edge[1]] = terminal_step.pk

        # taskを登録、または更新
        for edge in sprig.ad.edges:
            if edge in new_edges:
                task = Task()
            else:
                task = Task.objects.get(pk=sprig.ad.edges[edge]['pk'])

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

            task.save()

        return HttpResponseRedirect(reverse('index'))


add = CreateTask.as_view()


def all_previous(task):
    yield task
    previous = [_ for _ in Task.objects.all() if _.terminal_step == task.initial_step]
    for _ in previous:
        yield from all_previous(_)


def all_following(task):
    yield task
    following = [_ for _ in Task.objects.all() if task.terminal_step == _.initial_step]
    for _ in following:
        yield from all_following(_)


class DoneTask(View):
    """"""
    def get(self, req, id=None):
        this = Task.objects.get(pk=id)
        # 起点以前のタスクをすべて完了とする
        for task in all_previous(this):
            task.is_done = True
            task.save()
        return HttpResponseRedirect(reverse('index'))


done = DoneTask.as_view()


class UndoneTask(View):
    """"""
    def get(self, req, id=None):
        this = Task.objects.get(pk=id)
        # 起点以降のタスクをすべて未完了とする
        for task in all_following(this):
            task.is_done = False
            task.save()
        return HttpResponseRedirect(reverse('index'))


undone = UndoneTask.as_view()


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


class ShowRegisterForm(View):
    """"""

    DEFAULT_TEXT = """head_link] task1 :30- <5h30m> -16:00 @8888 (note)
    task2 /27- <2d4h> -/3 @7777 [tail_link (note)"""

    def get(self, req, default_text=DEFAULT_TEXT):
        context = {
            'default_text': default_text
        }
        return render(req, 'todo/register.html', context)

    def post(self, req, *args, **kwargs):
        return HttpResponseRedirect(reverse('register'))


register = ShowRegisterForm.as_view()


class Breakdown(ShowRegisterForm):
    """"""
    def __init__(self):
        ShowRegisterForm.__init__(self)

        self.default_text = """head_link] task1 :30- <5h30m> -16:00 @8888 (note)
    task2 /27- <2d4h> -/3 @7777 [tail_link (note)"""

    def get(self, req, id=None):
        # if False:
        #     pass
        if id:
            task = Task.objects.get(pk=id)
            default_text = task.restring()
        else:
            default_text = self.default_text
        context = {
            'default_text': default_text
        }
        return render(req, 'todo/register.html', context)

    def post(self, req, *args, **kwargs):
        return HttpResponseRedirect(reverse('breakdown'))


breakdown = Breakdown.as_view()