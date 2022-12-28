from django.urls import path

from . import views


app_name = 'accounts'
urlpatterns = [
    path('activation/<str:uidb64>/<str:token>/', views.ActivationView.as_view(), name='account_activation'),
    path('registration/', views.SignUpView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password/change/done/', views.ChangePasswordDoneView.as_view(),name='change_password_done'),
    path('password/reset/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('password/reset/done/', views.ResetPasswordDoneView.as_view(), name='reset_password_done'),
    path('password/reset/confirm/<str:uidb64>/<str:token>/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('password/reset/complete/', views.ResetPasswordCompleteView.as_view(), name='reset_password_complete'),
]
