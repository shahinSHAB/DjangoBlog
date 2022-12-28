from django.urls import path

from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='articles'),
    path('<int:page>/', views.ArticleListView.as_view(), name='articles'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('author/<str:username>/', views.AuthorInformationView.as_view(), name='author_detail'),
    path('profile/detail/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('category/<slug:slug>/', views.CategoryArticlesView.as_view(), name='category_articles'),
    path('category/<slug:slug>/<int:page>/', views.CategoryArticlesView.as_view(), name='category_articles'),
    path('articles/<slug:slug>/', views.ArticlesPeriodView.as_view(), name='articles_period'),
    path('articles/<slug:slug>/<int:page>/', views.ArticlesPeriodView.as_view(), name='articles_period'),
    path('articles/most-view/<slug:slug>/', views.MostViewedArticlesView.as_view(), name='most_viewed_articles'),
    path('articles/most-view/<slug:slug>/<int:page>/', views.MostViewedArticlesView.as_view(), name='most_viewed_articles'),
    path('panel/articles/', views.AllArticlesView.as_view(), name='panel'),
    path('panel/create/', views.ArticleCreateView.as_view(),name='article_create'),
    path('panel/<slug:slug>/preview/',
         views.ArticlePreView.as_view(), name='article_preview'),
    path('panel/update/<slug:slug>/',
         views.ArticleUpdateView.as_view(), name='article_update'),
    path('panel/delete/<slug:slug>/',
         views.ArticleDeleteView.as_view(), name='article_delete'),
    path('panel/category/create/', views.CategoryCreateView.as_view(),name='category_create'),
    path('panel/category/update/<slug:slug>/', views.CategoryUpdateView.as_view(),name='category_update'),
    path('panel/category/delete/<slug:slug>/', views.CategoryDeleteView.as_view(),name='category_delete'),
#     path('change-lang/', views.ChangeLanguageView.as_view(),name='change_language'),
]
