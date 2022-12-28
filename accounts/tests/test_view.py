from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TestViews(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@example.com',
            password='test1234'
        )
    
    # ----------- Test Custom Login View -----------
    def test_custom_login_view_url(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        
    def test_custom_login_view_url_name(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        
    def test_custom_login_view_correct_template(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertTemplateUsed(response, 'accounts/login.html')
           
    def test_custom_login_view(self):
        response = self.client.post(reverse('accounts:login'),data={
            'username':'test',
            'email':'test@example.com',
            'password':'test1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 1)
        
    # ----------- Test Custom Logout View -----------
    def test_custom_logout_view_url(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        
    def test_custom_logout_view_url_name(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        
    # def test_custom_login_view_correct_template(self):
    #     response = self.client.get(reverse('accounts:logout'))
    #     self.assertTemplateUsed(response, 'accounts/logout.html')
           
    def test_custom_logout_view(self):
        response = self.client.post(reverse('accounts:logout'),data={})
        self.assertEqual(response.status_code, 302)
        
    # ----------- Test SignUp View -----------
    def test_signup_view_url(self):
        response = self.client.get('/accounts/registration/')
        self.assertEqual(response.status_code, 200)
        
    def test_signup_view_url_name(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        
    def test_signup_view_correct_template(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertTemplateUsed(response, 'accounts/signup.html')
        
    # ----------- Test Change Password View -----------
    def test_change_password_view_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/accounts/password/change/')
        self.assertEqual(response.status_code, 200)
        
    def test_change_password_view_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('accounts:change_password'))
        self.assertEqual(response.status_code, 200)
        
    def test_change_password_view_correct_template(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('accounts:change_password'))
        self.assertTemplateUsed(response, 'accounts/change_password.html')
        
    def test_change_password_view_without_login(self):
        response = self.client.get(reverse('accounts:change_password'))
        self.assertEqual(response.status_code, 302)
        
    def test_change_password_view_with_login(self):
        self.client.login(username='test', password='test1234')
        response = self.client.post(reverse('accounts:change_password'),
                                    data={
                                        'old_password':'test1234',
                                        'new_password1':'test123456',
                                        'new_password2':'test123456',
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:change_password_done'))
    
    # ----------- Test Change Password Done View -----------
    def test_change_password_done_view_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/accounts/password/change/done/')
        self.assertEqual(response.status_code, 200)

    def test_change_password_done_view_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('accounts:change_password_done'))
        self.assertEqual(response.status_code, 200)

    def test_change_password_done_view_correct_template(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('accounts:change_password_done'))
        self.assertTemplateUsed(response, 'accounts/change_password_done.html')

    def test_change_password_done_view_without_login(self):
        response = self.client.get(reverse('accounts:change_password_done'))
        self.assertEqual(response.status_code, 302)
        
    def test_change_password_done_view_with_login(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('accounts:change_password_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your password Changed successfully')
        

        
        