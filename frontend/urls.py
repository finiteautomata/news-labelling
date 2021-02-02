from django.urls import path
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name="index" ),
    path('articles/<int:pk>/', views.ArticleView.as_view(), name='article_view'),
    path('next', views.NextArticleView.as_view(), name="next"),
    path('completed', views.CompletedView.as_view(), name="completed"),

    path('dashboard/', views.DashboardView.as_view(), name="dashboard_view"),
    path('dashboard/full_analysis', views.FullAnalysisView.as_view(), name="full_analysis_view"),
    path('batch/<str:batch_name>/', views.BatchView.as_view(), name="batch_view"),
    path('users/<str:username>/', views.UserView.as_view(), name='user_view'),
    path('users/<str:username>/labels/<int:article_pk>/', views.LabelView.as_view(), name="label_view"),

]
