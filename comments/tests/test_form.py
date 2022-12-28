from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from blog.models import Blog, Category
from ..forms import CommentForm
from ..models import Comment


class TestCommentForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        # small black gif
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        
        cls.user = get_user_model().objects.create_user(
            username='test',
            password='1234',
            email='test@example.com',
            is_author=True,
        )
        
        cls.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
        )

        cls.article = Blog.objects.create(
            title='First',
            slug='first',
            author=cls.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='small_blog_views_gif.gif',
                                         content=cls.small_gif,
                                         content_type='image/gif',
                                         ),
            view=1,
            publish=timezone.now(),
            code=10000,
            status=Blog.PUBLISH,
        )
        cls.article.category.add(cls.category)
        cls.article.save()

    # ---------- test comment form ----------
    def test_valid_comment_form(self):
        self.client.login(username='test', password='1234')
        form_data = {
            'name':'person',
            'text':'text',
            'publish':timezone.now(),
            'agree':1,
            'disagree':0,
        }
        form = CommentForm(data=form_data,**{'user':TestCommentForm.user,'article':TestCommentForm.article, 'parent':None})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().author, TestCommentForm.user)
        self.assertEqual(Comment.objects.first().article, TestCommentForm.article)
        self.assertEqual(Comment.objects.first().status, False)
        self.assertEqual(Comment.objects.first().agree, 0)      # because this is initialed field is disabled
        self.assertEqual(Comment.objects.first().reply, None)
        
    def test_invalid_comment_form(self):
        self.client.login(username='test', password='1234')
        form_data = {
            'name':'',
            'text':'text_1',
            'publish':timezone.now(),
            'reply':None,
            'agree':3,
            'disagree':1,
        }
        form = CommentForm(data=form_data,**{'user':TestCommentForm.user,'article':TestCommentForm.article, 'parent':None})
        self.assertFalse(form.is_valid())
        self.assertEqual(Comment.objects.count(), 0)