from time import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from blog.models import Blog, Category
from ..models import Comment


# ============= Test Comment Model ==============
class TestCommentModel(TestCase):

    def setUp(self):
        # small black gif
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@example.com',
            password='test1234',
            first_name='name',
            is_author=True,
        )

        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
        )

        self.article = Blog.objects.create(
            title='First',
            slug='first',
            author=self.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='small_blog_views_gif.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            view=1,
            publish=timezone.now(),
            code=10000,
            status=Blog.PUBLISH,
        )
        self.article.category.add(self.category)
        self.article.save()

        self.comment = Comment.objects.create(
            name='person',
            text='text',
            author=self.user,
            article=self.article,
            status=True,
            publish=timezone.now(),
            reply=None,
            agree=10,
            disagree=7,
        )

    def tearDown(self):
        for obj in Comment.objects.all():
            obj.delete()
        return super().tearDown()
    # --------- Test Comment Model ----------
    def test_comment_model(self):
        self.assertEqual(self.comment.name, 'person')
        self.assertEqual(self.comment.text, 'text')
        self.assertEqual(self.comment.author.username, self.user.username)
        self.assertEqual(self.comment.article.title, self.article.title)
        self.assertEqual(self.comment.status, True)
        self.assertEqual(self.comment.reply, None)
        self.assertEqual(self.comment.agree, 10)
        self.assertEqual(self.comment.disagree, 7)
        self.assertEqual(str(self.comment), 'person')
        self.assertTrue(isinstance(self.comment, Comment))
        self.assertEqual(self.comment.comment_replies(), 0)
        self.assertEqual(self.comment.published_replies(), 0)
        # self.assertEqual(self.comment.get_absolute_url(), '/comments/pk/')

    def test_comment_model_manager(self):
        self.assertEqual(
            Comment.objects.published().count(),
            Comment.objects.filter(status=True).count()
        )
        self.assertEqual(
            Comment.objects.parents().count(),
            Comment.objects.filter(reply=None).count()
        )


# ============= Test Comment Views =============
class TestCommentViews(TestCase):

    def setUp(self):
        # small black gif
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@example.com',
            password='test1234',
            first_name='name',
            is_author=True,
        )

        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
        )

        self.article = Blog.objects.create(
            title='First',
            slug='first',
            author=self.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='small_blog_views_gif.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            view=1,
            publish=timezone.now(),
            code=10000,
            status=Blog.PUBLISH,
        )
        self.article.category.add(self.category)
        self.article.save()

        self.comment = Comment.objects.create(
            name='person',
            text='text',
            author=self.user,
            article=self.article,
            status=True,
            publish=timezone.now(),
            reply=None,
            agree=10,
            disagree=7,
        )

        self.comment_1 = Comment.objects.create(
            name='person_1',
            text='text_1',
            author=self.user,
            article=self.article,
            status=False,
            publish=timezone.now(),
            reply=None,
            agree=5,
            disagree=12,
        )
        
    def tearDown(self):
        for CLASS in [Blog, Comment]:
            for obj in CLASS.objects.all():
                obj.delete()
        return super().tearDown()

    # ----------- test article comments view ------------
    def test_article_comments_view_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/comments/first/')
        self.assertEqual(response.status_code, 302)
        
    def test_article_comments_view_with_login_without_superuser(self):
        """User is authenticated but is not superuser
        should not access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/')
        self.assertEqual(response.status_code, 404)
        
    def test_article_comments_view_with_login_with_superuser(self):
        """User is authenticated and is superuser
        should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/')
        self.assertEqual(response.status_code, 200)
        
    def test_article_comments_view_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/')
        self.assertEqual(response.status_code, 200)

    def test_article_comments_view_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:article_comments', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_article_comments_view_correct_template(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:article_comments', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'comments/article_comments.html')

    def test_article_comments_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:article_comments', kwargs={'slug': 'first'}))
        # because of extra context
        self.assertContains(response, self.article.slug)
        self.assertContains(response, 'person')
        self.assertContains(response, 'person_1')
        self.assertEqual(len(response.context[1]['comments']), 2)

    # ----------- test published comments view ------------
    def test_published_comments_view_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/comments/published/first/')
        self.assertEqual(response.status_code, 302)

    def test_published_comments_view_with_login_without_superuser(self):
        """User is authenticated but is not superuser
        should not access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/published/first/')
        self.assertEqual(response.status_code, 404)

    def test_published_comments_view_with_login_with_superuser(self):
        """User is authenticated and is superuser
        should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/published/first/')
        self.assertEqual(response.status_code, 200)

    def test_published_comments_view_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/published/first/')
        self.assertEqual(response.status_code, 200)

    def test_published_comments_view_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:published_comments', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_published_comments_view_correct_template(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:published_comments', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'comments/published_comments.html')

    def test_published_comments_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:published_comments', kwargs={'slug': 'first'}))
        # because of extra context
        self.assertContains(response, self.article.slug)
        self.assertContains(response, 'person')
        # because this comment was not publish
        self.assertNotContains(response, 'person_1')
        self.assertEqual(len(response.context[1]['comments']), 1)

    # ----------- test comment detail view ----------
    def test_comment_detail_view_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/comments/first/1/detail/')
        self.assertEqual(response.status_code, 302)
        
    def test_comment_detail_view_with_login_without_superuser(self):
        """User is authenticated but is not superuser should not
        access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/detail/')
        self.assertEqual(response.status_code, 404)
        
    def test_comment_detail_view_with_login_with_superuser(self):
        """User is authenticated and is superuser should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/detail/')
        self.assertEqual(response.status_code, 200)
        
    def test_comment_detail_view_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/detail/')
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_view_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:detail', kwargs={'slug': 'first', 'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_view_correct_template(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:detail', kwargs={'slug': 'first', 'pk': 1}))
        self.assertTemplateUsed(response, 'comments/comment_detail.html')

    def test_comment_detail_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:detail', kwargs={'slug': 'first', 'pk': 1}))
        self.assertEqual(response.context[1]
                         ['comment'].name, self.comment.name)
        self.assertContains(response, 'text')
        self.assertContains(response, 'person')
        self.assertContains(response, 10)
        self.assertContains(response, 7)

    # ----------- test comment create view ----------
    def test_comment_create_view_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/comments/first/create/')
        self.assertEqual(response.status_code, 302)
        
    def test_comment_create_view_with_login(self):
        """User is authenticated should access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/create/')
        self.assertEqual(response.status_code, 200)
        
    def test_comment_create_view_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/create/')
        self.assertEqual(response.status_code, 200)

    def test_comment_create_view_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:create', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_comment_create_view_correct_template(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:create', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'comments/comment_create.html')

    def test_comment_create_view(self):
        self.client.login(username='test', password='test1234')
        response = self.client.post(reverse('comments:create', kwargs={'slug': 'first'}),
        data={
            'name': 'person_3',
            'text': 'text_3',
            'publish': timezone.now(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertRedirects(response, reverse(
            'blog:detail', kwargs={'slug': 'first'}))
        self.assertEqual(Comment.objects.first().name, 'person_3')
        self.assertEqual(Comment.objects.first().reply, None)
        self.assertEqual(Comment.objects.first().text, 'text_3')
        self.assertEqual(Comment.objects.first().agree, 0)
        
    def test_comment_create_view_with_parent_comment(self):
        self.client.login(username='test', password='test1234')
        response = self.client.post(reverse('comments:create', kwargs={'slug': 'first', 'name':'person'}),
        data={
            'name': 'person_4',
            'text': 'text_4',
            'publish': timezone.now(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertRedirects(response, reverse(
            'blog:detail', kwargs={'slug': 'first'}))
        self.assertEqual(Comment.objects.first().name, 'person_4')
        self.assertEqual(Comment.objects.first().reply, self.comment)  # because have parent name in reply
        self.assertEqual(Comment.objects.first().text, 'text_4')
        self.assertEqual(Comment.objects.first().agree, 0)

    # ----------- test comment update view ----------
    def test_comment_update_view_without_login(self):
        """User is not authenticated should  not access the page
        """
        response = self.client.get('/comments/first/1/update/')
        self.assertEqual(response.status_code, 302)

    def test_comment_update_view_with_login_without_superuser(self):
        """User is authenticated but is not superuser
        should not access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/update/')
        self.assertEqual(response.status_code, 404)
        
    def test_comment_update_view_with_login_with_superuser(self):
        """User is authenticated and is superuser
        should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/update/')
        self.assertEqual(response.status_code, 200)
        
    def test_comment_update_view_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/update/')
        self.assertEqual(response.status_code, 200)

    def test_comment_update_view_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:update', kwargs={'slug': 'first', 'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_comment_update_view_correct_template(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:update', kwargs={'slug': 'first', 'pk': 1}))
        self.assertTemplateUsed(response, 'comments/comment_update.html')

    def test_comment_update_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.post(reverse('comments:update', kwargs={'slug': 'first', 'pk': 1}),
        data={
            'name': 'personUpdate1',
            'text': 'textUpdated1',
            'author':1,
            'article':1,
            'status':True,
            'publish':self.comment.publish,
            'reply':'',
            'agree':5,
            'disagree':3,
        })
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'comments:detail', kwargs={'slug': 'first', 'pk': 1}))
        self.assertEqual(Comment.objects.last().text, 'textUpdated1')
        self.assertNotEqual(Comment.objects.last().text, 'text')    # not equal because comment updated
        self.assertEqual(Comment.objects.last().name, 'personUpdate1')
        self.assertEqual(Comment.objects.last().agree, 5)
        self.assertEqual(Comment.objects.last().disagree, 3)

    # ----------- test comment delete view ----------
    def test_comment_delete_view_without_login(self):
        """User is not authenticated should  not access the page
        """
        response = self.client.get('/comments/first/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_comment_delete_view_with_login_without_superuser(self):
        """User is authenticated but is not superuser
        should not access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/delete/')
        self.assertEqual(response.status_code, 404)

    def test_comment_delete_view_with_login_with_superuser(self):
        """User is authenticated and is superuser
        should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/1/delete/')
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_view_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get('/comments/first/2/delete/')
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_view_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:delete', kwargs={'slug': 'first', 'pk': 2}))
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_view_correct_template(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('comments:delete', kwargs={'slug': 'first', 'pk': 2}))
        self.assertTemplateUsed(response, 'comments/comment_delete.html')

    def test_comment_delete_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='test1234')
        response = self.client.post(reverse('comments:delete', kwargs={
                                    'slug': 'first', 'pk': 2}), data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'comments:article_comments', kwargs={'slug': 'first'}))
        self.assertEqual(Comment.objects.count(), 1)
