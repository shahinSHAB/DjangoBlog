from django.test import TestCase
from django.contrib.auth import get_user_model


# ============ Test Custom User Model ============
class TestCustomUser(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@example.com',
            password='1234test',
            is_author=True
        )
        self.super_user = get_user_model().objects.create_superuser(
            username='super',
            email='super@example.com',
            password='super1234',
            gender='m'
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, 'test')
        self.assertEqual(self.user.pk, self.user.id)
        self.assertEqual(self.user.id, 1)
        self.assertEqual(self.user.email, 'test@example.com')

    def test_create_superuser(self):
        self.assertEqual(self.super_user.username, 'super')
        self.assertEqual(self.super_user.pk, self.super_user.id)
        self.assertEqual(self.super_user.id, 2)
        self.assertEqual(self.super_user.email, 'super@example.com')
        
    def test_custom_user_manager(self):
        self.assertEqual(get_user_model().objects.filter(is_author=True).first().username,    
                         get_user_model().objects.author_users().first().username)
        self.assertEqual(get_user_model().objects.filter(gender='m').count(), 1)
        self.assertEqual(get_user_model().objects.filter(gender='m').count(),
                         get_user_model().objects.male_users().count())
        self.assertEqual(get_user_model().objects.filter(gender='f').count(), 0)     # because there is not any female user
        self.assertEqual(get_user_model().objects.filter(gender='f').count(),
                         get_user_model().objects.female_users().count())
        self.assertEqual(get_user_model().objects.filter(is_active=True).first().username,
                         get_user_model().objects.active_users().first().username)
