from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('done/<int:id>', views.done, name='done'),
    path('undone/<int:id>', views.undone, name='undone'),
    path('show_around_1/<int:id>', views.show_around_1, name='show_around_1'),
    path('show_buds', views.show_buds, name='show_buds'),
    path('show_trunk', views.show_trunk, name='show_trunk'),
    path('register', views.register, name='register'),
    path('breakdown/<int:id>', views.breakdown, name='breakdown'),
]