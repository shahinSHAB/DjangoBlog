from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Blog, Category
from ..forms import BLogForm, CategoryForm

MODELS = [Blog, Category,]


# =============== Test Forms ==================
class TestFormModels(TestCase):

    def setUp(self):
        # small black gif
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        self.user = get_user_model().objects.create_user(
            username='test',
            password='1234',
            email='test@example.com',
            is_author=True,
        )
        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
        )
        self.category_1 = Category.objects.create(
            title='Test1 Category',
            slug='test1-category',
            position=2,
            status = True
        )

    def tearDown(self):
        """Depopulate created model instances from test database."""
        for model in MODELS:
            for obj in model.objects.all():
                obj.delete()

    # ------------- Test Blog Form ------------
    def test_blog_form_valid(self):
        form_data = {
            'title': 'Form Title',
            'slug': 'form-title',
            'author':self.user,
            'content': 'form content',
            'code': 122335,
            'special': True,
            'publish': '2022-10-08 13:52:16',
            'category': [2,],   # because category must be with True status
            'status':'p',
        }
        form_files = {'thumbnail': SimpleUploadedFile(name='small_form2_valid.gif',
                                                      content=self.small_gif,
                                                      content_type='image/gif',
                                                      ), }
        form = BLogForm(data=form_data, files=form_files, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Blog.objects.count(), 1)

    def test_blog_form_invalid(self):
        form_data = {
            'title': 'Form Title',
            'slug': 'form-title',
            'author': 1,
            'content': 'form content',
            'code': 122335,
            'special': True,
            'publish': '2022-10-08 13:52:16',
            'category': '',
        }
        form_files = {'thumbnail': SimpleUploadedFile(name='small_form3_valid.gif',
                                                      content=self.small_gif,
                                                      content_type='image/gif',
                                                      ), }
        form = BLogForm(data=form_data, files=form_files, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(Blog.objects.count(), 0)

    # ------------- Test Category Form ------------
    def test_category_form_valid(self):
        data = {
            'title': 'Planet',
            'slug': 'planet',
            'position': 5,
            'parent': '',
            'status': True,
        }
        form = CategoryForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Category.objects.count(), 3)

    def test_category_form_invalid(self):
        data = {
            'title': 'Planet',
            'slug': '',
            'position': 5,
            'parent': '',
            'status': True,
        }
        form = CategoryForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(Category.objects.count(), 2)
