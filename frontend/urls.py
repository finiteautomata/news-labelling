from django.urls import path
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name="index" ),
    path('articles/<int:pk>/', views.ArticleView.as_view(), name='article_view'),
    path('labels/<str:username>/<int:article_pk>/', views.LabelView.as_view(), name="label_view"),
    path('next', views.NextArticleView.as_view(), name="next"),
    path('completed', views.CompletedView.as_view(), name="completed"),
    path('stats', views.StatisticsView.as_view(), name="stats")
]
