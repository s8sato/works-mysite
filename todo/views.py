from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import Post
from .forms import PostForm


def index(req):
    posts = Post.objects.all()
    form = PostForm()
    context = {'posts': posts, 'form': form, }
    return render(req, 'todo/index.html', context)


def add(req):
    form = PostForm(req.POST)
    form.save(commit=True)
    return HttpResponseRedirect(reverse('index'))


def delete(req, id=None):
    post = get_object_or_404(Post, pk=id)
    post.delete()
    return HttpResponseRedirect(reverse('index'))