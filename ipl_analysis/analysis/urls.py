from django.urls import path
from . import views

app_name = 'analysis_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search_player/', views.search_player, name='search_player'),
    path('test_mongodb/', views.test_mongodb, name='test_mongodb'),
]
