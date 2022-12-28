from django.urls import path

from . import views

app_name='comments'

urlpatterns = [
    path('<slug:slug>/', views.ArticleCommentsView.as_view(), name='article_comments'),
    path('published/<slug:slug>/', views.PublishedCommentsView.as_view(), name='published_comments'),
    path('<slug:slug>/create/', views.CommentCreateView.as_view(), name='create'),
    path('<slug:slug>/create/<str:name>', views.CommentCreateView.as_view(), name='create'),
    path('<slug:slug>/<int:pk>/detail/', views.CommentDetailView.as_view(), name='detail'),
    path('<slug:slug>/<int:pk>/update/', views.CommentUpdateView.as_view(), name='update'),
    path('<slug:slug>/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='delete'),
]