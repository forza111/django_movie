from django.shortcuts import render,redirect
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Movie, Category, Actor, Genre
from .forms import ReviewForm, RatingForm


class GenreYear():
    '''Жанры и годы выхода фильмов'''
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year")


class MoviesView(GenreYear,ListView):
    '''Список фильмов'''
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    paginate_by = 1
    #template_name джанго в данном случае генерирует автоматически имя модели Movie + list


class MovieDetailView(GenreYear,DetailView):
    '''Полное описание фильма'''
    model = Movie
    slug_field = 'url' #по какому полю нужно искать нашу запись
    #template_name джанго в данном случае генерирует автоматически имя модели Movie + detail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        return context

    
class AddReview(View):
    '''Отзывы'''
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear,DetailView):
    '''Вывод информации об актере'''
    model = Actor
    template_name = "movies/actor.html"
    slug_field = "name"


class FilterMoviesView(GenreYear,ListView):
    '''Фльтр фильмов'''
    paginate_by = 2

    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(FilterMoviesView, self).get_context_data(*args, **kwargs)
        context['year'] = ''.join([f"year{x}&" for x in self.request.GET.getlist("year")])
        context['genre'] = ''.join([f"genre{x}&" for x in self.request.GET.getlist("genre")])
        return context

class AddStarRating(View):
    '''Добавление рейтинга к фльму'''
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)

class Search(ListView):
    '''Поск фльмов'''
    paginate_by = 2

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super(Search, self).get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context