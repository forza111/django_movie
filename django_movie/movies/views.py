from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic import ListView, DetailView


from .models import Movie

class MoviesView(ListView):
    '''Список фильмов'''
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    template_name = 'movies/movies.html'


class MovieDetailView(DetailView):
    '''Полное описание фильма'''
    model = Movie
    slug_field = 'url' #по какому полю нужно искать нашу запись
    #template_name джанго в данном случае генерирует автоматически имя модели Movie + detail

