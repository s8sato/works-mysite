from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('show_around_1/<int:id>', views.show_around_1, name='show_around_1'),
    path('show_buds', views.show_buds, name='show_buds'),
]