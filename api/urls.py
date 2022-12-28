from django.urls import path, include

from rest_framework import routers

from . import views


app_name = 'api'
router = routers.SimpleRouter()
router.register('users', views.UserApiView, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/articles/', views.ArticleListApiView.as_view(), name='published_articles'),
    path('v1/articles-period/<slug:slug>/', views.ArticlesPeriodApiView.as_view(), name='articles_period'),
    path('v1/articles-most-view/<slug:slug>/', views.MostViewedArticlesApiView.as_view(), name='most_viewed_articles'),
    path('v1/articles/<slug:slug>/', views.ArticleDetailApiView.as_view(), name='article_detail'),
    path('v1/category/<slug:slug>/', views.CategoryArticlesApiView.as_view(), name='category_articles'),
    path('v1/author/<str:username>/', views.AuthorInformationApiView.as_view(), name='author_information'),
    path('v1/profile/detail/<str:username>/', views.ProfileDetailApiView.as_view(), name='profile_detail'),
    path('v1/profile/update/<str:username>/', views.ProfileUpdateApiView.as_view(), name='profile_update'),
    path('v1/admin-panel/', views.AllArticlesApiView.as_view(), name='all_articles'),
    path('v1/admin-panel/create/', views.CreateArticleApiView.as_view(), name='article_create'),
    path('v1/admin-panel/detail/<slug:slug>/', views.ArticleDetailUpdateDeleteApiView.as_view(),
         name='update_delete_article'),
    path('v1/admin-panel/category/create/',views.CreateCategoryApiView.as_view(), name='category_create'),
    path('v1/admin-panel/category/detail/<slug:slug>/',views.CategoryDetailUpdateDeleteApiView.as_view(),
         name='update_delete_category'),
    path('v1/comments/<slug:slug>/', views.ArticleCommentsApiView.as_view(), name='article_comments'),
    path('v1/comments/published/<slug:slug>/', views.PublishedCommentsApiView.as_view(), name='published_comments'),
    path('v1/comments/<slug:slug>/<int:pk>/detail/', views.CommentDetailApiView.as_view(), name='comment_detail'),
    path('v1/comments/<slug:slug>/create/', views.CommentCreateApiView.as_view(), name='comment_create'),
    path('v1/comments/<slug:slug>/<int:pk>/update/', views.CommentUpdateApiView.as_view(), name='comment_update'),
    path('v1/comments/<slug:slug>/<int:pk>/delete/', views.CommentDeleteApiView.as_view(), name='comment_delete'),
]
