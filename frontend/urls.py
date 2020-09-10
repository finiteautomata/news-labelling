from django.urls import path
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name="index" ),
    path('articles/<int:pk>/', views.ArticleView.as_view(), name='article_view'),
]
