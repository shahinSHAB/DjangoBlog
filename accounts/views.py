from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.auth import get_user_model, logout
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm
from .models import CustomUser
from . import mixins


# =========== Custom Login View ============
class CustomLoginView(mixins.AuthenticateOrRedirectMixins, SuccessMessageMixin, LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('blog:articles')
    success_message = 'You logged in successfully'

    def get_redirect_url(self):
        return self.success_url


# =========== Custom Logout View ============
class CustomLogoutView(LogoutView):
    # template_name = 'accounts/logout.html'
    
    def get(self, request, *args, **kwargs):
        messages.success(request, 'You logged out successfully')
        return super().get(request, *args, **kwargs)
        
    def get_redirect_url(self):
        return reverse_lazy('accounts:login')
 
    
# ============== SignUp View ===============
class SignUpView(mixins.AuthenticateOrRedirectMixins, generic.CreateView):
    model = get_user_model()
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        email_subject = 'activation Account'
        current_site = get_current_site(self.request)
        email_message = render_to_string('accounts/email_message.html', context={
            'user':user,
            'uidb64':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),
            'domain': current_site.domain
        })
        to_email = form.cleaned_data['email']
        mail_to_user = EmailMessage(
            email_subject, email_message, to=(to_email,)
        )
        mail_to_user.send()
        return HttpResponse('<p style="text-align:center;font-size:194%;color:whitesmoke;background-color:black;padding:4% 1%;width:81%;margin:34vh auto 0 auto;border-radius:5px;font-weight:lighter;"> Thank You for SignUp. your activation account link was send successfully, please go to your emails and confirm it</p>')
 
    
# ============== Change Password View ===============
class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:change_password_done')


# ============== Change Password Done View ===============
class ChangePasswordDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/change_password_done.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = super().dispatch(request, *args, **kwargs)
        logout(request)
        return obj
    

# ============== Reset Password View ===============
class ResetPasswordView(mixins.AuthenticateOrRedirectMixins, PasswordResetView):
    template_name = 'accounts/reset_password.html'
    success_url = reverse_lazy('accounts:reset_password_done')
    email_template_name = 'accounts/reset_password_email.html'
    

# ============== Reset Password Done View ===============
class ResetPasswordDoneView(mixins.AuthenticateOrRedirectMixins, PasswordResetDoneView):
    template_name = 'accounts/reset_password_done.html'


# ============== Reset Password Confirm View ===============
class ResetPasswordConfirmView(mixins.AuthenticateOrRedirectMixins, PasswordResetConfirmView):
    template_name = 'accounts/reset_password_confirm.html'
    success_url = reverse_lazy('accounts:reset_password_complete')


# ============== Reset Password Complete View ===============
class ResetPasswordCompleteView(mixins.AuthenticateOrRedirectMixins, PasswordResetCompleteView):
    template_name = 'accounts/reset_password_complete.html'


# ============= activation View ==============
class ActivationView(generic.TemplateView):
    template_name = 'accounts/account_activation.html'
    
    def get(self, request, *args, **kwargs):
        user_id_b64 = kwargs.get('uidb64')
        user_id = force_str(urlsafe_base64_decode(user_id_b64))
        token = kwargs.get('token')
        try:
            user = get_user_model().objects.get(id=user_id)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if  user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse('<p style="text-align:center;font-size:194%;color:whitesmoke;background-color:black;padding:4% 1%;width:81%;margin:34vh auto 0 auto;border-radius:5px;font-weight:lighter;">well done. you registered successfully.</p>')
        else:
            return HttpResponse('<p style="text-align:center;font-size:194%;color:whitesmoke;background-color:black;padding:4% 1%;width:81%;margin:34vh auto 0 auto;border-radius:5px;font-weight:lighter;">Sorry. your activation link is expire, please register again from <a href="/accounts/registration/">here</a></p>')
