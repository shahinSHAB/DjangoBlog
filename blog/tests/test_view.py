from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta

from ..models import Blog, Category, IpAddress

MODELS = [Blog, Category,]


# ============= Test Blog Views ===============
class TestBlogViews(TestCase):

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
        self.user_2 = get_user_model().objects.create_user(
            username='test2',
            email='test2@example.com',
            password='test12345',
            first_name='name2',
            is_author=True,
        )
        
        self.ip_address = IpAddress.objects.create(ip_address='127.0.0.5')

        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
            status=True,
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
            publish=timezone.now() - timedelta(days=12),
            code=10000,
            status=Blog.PUBLISH,
        )
        self.article.hits.add(self.ip_address)
        self.article.category.add(self.category)
        self.article.save()
        
        self.article_2 = Blog.objects.create(
            title='Second',
            slug='second',
            author=self.user_2,
            content='something new',
            thumbnail=SimpleUploadedFile(name='small_two_blog_views_gif.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            view=5,
            code=10040,
            status=Blog.PUBLISH,
        )
        self.article.hits.add(self.ip_address)
        self.article.category.add(self.category)
        self.article.save()
        
        self.article_3 = Blog.objects.create(
            title='Third',
            slug='third',
            author=self.user_2,
            content='something new third',
            thumbnail=SimpleUploadedFile(name='small_three_blog_views_gif.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            view=3,
            code=13040,
            status=Blog.DRAFT,
        )
        self.article.hits.add(self.ip_address)
        self.article.category.add(self.category)
        self.article.save()

    def tearDown(self):
        """Depopulate created model instances from test database."""
        for model in MODELS:
            for obj in model.objects.all():
                obj.delete()

    # --------- ArticleListView -----------
    def test_article_list_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_article_list_url_name(self):
        response = self.client.get(reverse('blog:articles'))
        self.assertEqual(response.status_code, 200)

    def test_article_list_template_correct(self):
        response = self.client.get(reverse('blog:articles'))
        self.assertTemplateUsed(response, 'blog/article_list.html')

    def test_article_list_content_without_search_query(self):
        response = self.client.get(reverse('blog:articles'))
        self.assertContains(response, 'something')
        self.assertEqual(Blog.objects.count(), 3)
        
    def test_article_list_content_with_correct_search_query(self):
        response = self.client.get('/?q=first')
        self.assertContains(response, 'something')
        self.assertEqual(response.status_code, 200)
        
    def test_article_list_content_with_not_correct_search_query(self):
        response = self.client.get('/?q=false')
        self.assertEqual(response.status_code, 404)

    # ---------- AllArticlesView ----------
    def test_all_article_list_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/articles/')
        self.assertEqual(response.status_code, 302)
        
    def test_all_article_list_with_login_without_author(self):
        """User is authenticated but is not author 
        should not access the page
        """
        self.user.is_author = False
        self.user.save()
        self.client.login(username='test', password='test1234')       
        response = self.client.get('/panel/articles/')
        self.assertEqual(response.status_code, 404)
        
    def test_all_article_list_with_login_with_author(self):
        """User is authenticated and is author 
        should access the page
        """
        # user is author by default
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/articles/')
        self.assertEqual(response.status_code, 200)
        
    def test_all_article_list_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/articles/')
        self.assertEqual(response.status_code, 200)

    def test_all_article_list_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:panel'))
        self.assertEqual(response.status_code, 200)

    def test_all_article_list_template_correct(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:panel'))
        self.assertTemplateUsed(response, 'admin_panel/index.html')

    def test_all_article_list_get_request(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:panel'))
        self.assertContains(response, 'something')
        self.assertEqual(Blog.objects.count(), 3)

    # --------- ArticleDetailView ----------
    def test_article_detail_before_view(self):
        self.assertEqual(self.article.view, 1)
        self.assertEqual(self.article.hits.count(), 1)
        
    def test_article_detail_after_view(self):
        self.client.get('/first/')
        self.article.refresh_from_db()
        self.assertEqual(self.article.view, 2)
        self.assertEqual(self.article.hits.count(), 2)
        
    def test_article_detail_url(self):
        response = self.client.get('/first/')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_url_name(self):
        response = self.client.get(
            reverse('blog:detail', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_article_detail_template_correct(self):
        response = self.client.get(
            reverse('blog:detail', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'blog/article_detail.html')

    def test_article_detail_get_request(self):
        response = self.client.get(
            reverse('blog:detail', kwargs={'slug': 'first'}))
        self.assertContains(response, 'First')

    # ---------- ArticleCreateView ------------         
    def test_article_create_without_login(self):
        """User is not authenticated should not access the page
        """                  
        response = self.client.get('/panel/create/')    
        self.assertEqual(response.status_code, 302)
        
    def test_article_create_with_login_without_author(self):
        """User is authenticated but is not author
        should not access the page
        """
        self.user.is_author = False
        self.user.save()
        self.client.login(username='test', password='test1234')                  
        response = self.client.get('/panel/create/')    
        self.assertEqual(response.status_code, 404)
        
    def test_article_create_with_login_with_author(self):
        """User is authenticated and is author
        should access the page
        """
        # user is author by default
        self.client.login(username='test', password='test1234')                  
        response = self.client.get('/panel/create/')    
        self.assertEqual(response.status_code, 200)
        
    def test_article_create_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/create/')    
        self.assertEqual(response.status_code, 200)

    def test_article_create_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:article_create'))
        self.assertEqual(response.status_code, 200)

    def test_article_create_correct_template(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:article_create'))
        self.assertTemplateUsed(response, 'admin_panel/article_create.html')

    # def test_article_create_post_request(self):             # dont work and fails
    #     file = {'thumbnail': '/media/images/anime_girl_14-wallpaper-1920x1080.jpg', }
    #     response = self.client.post(reverse('blog:article_create'), data={
    #         'title': 'Create Title',
    #         'slug': 'create-title',
    #         'author': 1,
    #         'content': 'create content',
    #         'code': 16086,
    #         'view':0,
    #         'status':'d',
    #         'special': True,
    #         'publish': '2022-11-01 15:58:07',
    #         'category': [1,],
    #     },files=file)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Blog.objects.count(), 2)

    # ---------- ArticleUpdateView ------------
    def test_article_update_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/update/first/')
        self.assertEqual(response.status_code, 302)

    def test_article_update_with_login_without_owner_with_draft(self):
        """User is authenticated and status of article is 'd' or
        'b' but user is not owner should not access the page
        """
        # login with user and article is Third
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/update/third/')
        self.assertEqual(response.status_code, 404)

    def test_article_update_with_login_with_owner_without_draft(self):
        """User is authenticated and user is owner but
        status of article is not 'd' or 'b' should not access the page
        """
        # login with user_2 and article is Second
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/update/second/')
        self.assertEqual(response.status_code, 404)

    def test_article_update_with_login_with_owner_with_draft(self):
        """User is authenticated and user is owner but
        status of article is not 'd' or 'b' should not access the page
        """
        # login with user_2 and article is Third
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/update/third/')
        self.assertEqual(response.status_code, 200)

    def test_article_update_url(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/update/third/')
        self.assertEqual(response.status_code, 200)

    def test_article_update_url_name(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get(
            reverse('blog:article_update', kwargs={'slug': 'third'}))
        self.assertEqual(response.status_code, 200)

    def test_article_update_correct_template(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get(
            reverse('blog:article_update', kwargs={'slug': 'third'}))
        self.assertTemplateUsed(response, 'admin_panel/article_update.html')

    def test_article_update_post_request(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.post(reverse('blog:article_update', kwargs={'slug': 'third'}), data={
            'title': 'Update',
            'slug': 'update',
            'author': 1,
            'content': 'update content',
            'code': 10509,
            'special': True,
            'category': [1,],
            'publish': '2022-10-08 14:59:16',
            'status':'d'
        }, files={'thumbnail': '/media/images/small_blog_views_gif.gif'})
        self.article.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Blog.objects.last().title, 'Update')
        self.assertEqual(Blog.objects.last().slug, 'update')
        self.assertEqual(Blog.objects.last().code, 10509)
        self.assertEqual(Blog.objects.last().status, 'd')
        self.assertNotEqual(Blog.objects.last().status, 'p')

    # ---------- ArticleDeleteView ------------
    def test_article_delete_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/delete/first/')
        self.assertEqual(response.status_code, 302)
        
    def test_article_delete_with_login_without_owner_with_draft(self):
        """User is authenticated and status of article is 'd' or
        'b' but user is not owner should not access the page
        """
        # login with user and article is Third
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/delete/third/')
        self.assertEqual(response.status_code, 404)
        
    def test_article_delete_with_login_with_owner_without_draft(self):
        """User is authenticated and user is owner but
        status of article is not 'd' or 'b' should not access the page
        """
        # login with user_2 and article is Second
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/delete/second/')
        self.assertEqual(response.status_code, 404)
        
    def test_article_delete_with_login_with_owner_with_draft(self):
        """User is authenticated and user is owner but
        status of article is not 'd' or 'b' should not access the page
        """
        # login with user_2 and article is Third
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/delete/third/')
        self.assertEqual(response.status_code, 200)
        
    def test_article_delete_url(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/delete/third/')
        self.assertEqual(response.status_code, 200)

    def test_article_delete_url_name(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get(
            reverse('blog:article_delete', kwargs={'slug': 'third'}))
        self.assertEqual(response.status_code, 200)

    def test_article_delete_correct_template(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get(
            reverse('blog:article_delete', kwargs={'slug': 'third'}))
        self.assertTemplateUsed(response, 'admin_panel/article_delete.html')

    def test_article_delete_get_request(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.get(
            reverse('blog:article_delete', kwargs={'slug': 'third'}))
        self.assertContains(
            response, 'Are you sure you want to delete "Third" ?')

    def test_article_delete_post_request(self):
        self.client.login(username='test2', password='test12345')
        response = self.client.post(reverse('blog:article_delete', kwargs={
                                    'slug': 'third'}), data={'slug': 'third'})
        self.assertEqual(response.status_code, 302)


    # --------- ArticlesPeriodView -----------
    # last-month period
    def test_articles_period_last_month_url(self):
        response = self.client.get('/articles/last-month/')
        self.assertEqual(response.status_code, 200)
        
    def test_articles_period_last_month_url_name(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug':'last-month'}))
        self.assertEqual(response.status_code, 200)

    def test_articles_period_last_month_template_correct(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-month'}))
        self.assertTemplateUsed(response, 'blog/articles_period.html')

    def test_articles_period_last_month_content(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-month'}))
        self.assertContains(response, 'First')
        
    # last-week period
    def test_articles_period_last_week_url(self):
        response = self.client.get('/articles/last-week/')
        self.assertEqual(response.status_code, 200)
        
    def test_articles_period_last_week_url_name(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug':'last-week'}))
        self.assertEqual(response.status_code, 200)  

    def test_articles_period_last_week_template_correct(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-week'}))
        self.assertTemplateUsed(response, 'blog/articles_period.html')

    def test_articles_period_last_week_content(self):
        response = self.client.get(
            reverse('blog:articles_period', kwargs={'slug': 'last-week'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second')
        self.assertNotContains(response, 'First')   # because article is older than week
        
    # last-day period
    def test_articles_period_last_day_url(self):
        response = self.client.get('/articles/last-day/')
        self.assertEqual(response.status_code, 200)
        
    def test_articles_period_last_day_url_name(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug':'last-day'}))
        self.assertEqual(response.status_code, 200)

    def test_articles_period_last_day_template_correct(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-day'}))
        self.assertTemplateUsed(response, 'blog/articles_period.html')

    def test_articles_period_last_day_content(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-day'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second')
        self.assertNotContains(response, 'First')  # because article is older than day
        
    # last-five_articles period
    def test_articles_period_last_five_articles_url(self):
        response = self.client.get('/articles/last-five-articles/')
        self.assertEqual(response.status_code, 200)
        
    def test_articles_period_last_five_articles_url_name(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug':'last-five-articles'}))
        self.assertEqual(response.status_code, 200)

    def test_articles_period_last_five_articles_template_correct(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-five-articles'}))
        self.assertTemplateUsed(response, 'blog/articles_period.html')

    def test_articles_period_last_five_articles_content(self):
        response = self.client.get(reverse('blog:articles_period', kwargs={'slug': 'last-five-articles'}))
        self.assertContains(response, 'something')
    
    # articles-period not-correct-url 
    def test_articles_period_not_correct_url(self):
        response = self.client.get('/articles/last-something/')
        self.assertEqual(response.status_code, 404)
        
    # --------- Most Viewed Articles View-----------
    # last-month period most-view
    def test_most_viewed_articles_last_month_url(self):
        response = self.client.get('/articles/most-view/last-month/')
        self.assertEqual(response.status_code, 200)
        
    def test_most_viewed_articles_last_month_url_name(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug':'last-month'}))
        self.assertEqual(response.status_code, 200)

    def test_most_viewed_articles_last_month_template_correct(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-month'}))
        self.assertTemplateUsed(response, 'blog/most_viewed_articles.html')

    def test_most_viewed_articles_last_month_content(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-month'}))
        self.assertContains(response, 'First')
        self.assertEqual(response.context[2]['articles'][0].title, 'Second')   # because of view ordering
        self.assertEqual(response.context[2]['articles'][1].title, 'First')
        
    # last-week period most-view
    def test_most_viewed_articles_last_week_url(self):
        response = self.client.get('/articles/most-view/last-week/')
        self.assertEqual(response.status_code, 200)
        
    def test_most_viewed_articles_last_week_url_name(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug':'last-week'}))
        self.assertEqual(response.status_code, 200)  

    def test_most_viewed_articles_last_week_template_correct(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-week'}))
        self.assertTemplateUsed(response, 'blog/most_viewed_articles.html')

    def test_most_viewed_articles_last_week_content(self):
        response = self.client.get(
            reverse('blog:most_viewed_articles', kwargs={'slug': 'last-week'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second')
        self.assertNotContains(response, 'First')   # because article is older than week
        
    # last-day period most-view
    def test_most_viewed_articles_last_day_url(self):
        response = self.client.get('/articles/most-view/last-day/')
        self.assertEqual(response.status_code, 200)
        
    def test_most_viewed_articles_last_day_url_name(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug':'last-day'}))
        self.assertEqual(response.status_code, 200)

    def test_most_viewed_articles_last_day_template_correct(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug':'last-day'}))
        self.assertTemplateUsed(response, 'blog/most_viewed_articles.html')

    def test_most_viewed_articles_last_day_content(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-day'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second')
        self.assertNotContains(response, 'First')  # because article is older than a day
        
    # last-five_articles period most-view
    def test_most_viewed_articles_last_five_articles_url(self):
        response = self.client.get('/articles/most-view/last-five-articles/')
        self.assertEqual(response.status_code, 200)
        
    def test_most_viewed_articles_last_five_articles_url_name(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug':'last-five-articles'}))
        self.assertEqual(response.status_code, 200)

    def test_most_viewed_articles_last_five_articles_template_correct(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-five-articles'}))
        self.assertTemplateUsed(response, 'blog/most_viewed_articles.html')

    def test_most_viewed_articles_last_five_articles_content(self):
        response = self.client.get(reverse('blog:most_viewed_articles', kwargs={'slug': 'last-five-articles'}))
        self.assertContains(response, 'something')
        self.assertEqual(response.context[2]['articles'][0].title, 'Second')    # because of view ordering
        self.assertEqual(response.context[2]['articles'][1].title, 'First')
    
    # most-viewed-articles not-correct-url 
    def test_most_viewed_articles_not_correct_url(self):
        response = self.client.get('/articles/most-view/last-something/')
        self.assertEqual(response.status_code, 404)
        
    # -------------- Profile Detail View ---------------
    def test_profile_detail_view_without_login(self):
        """user not authenticated should not access
        and redirect to login page
        """
        response = self.client.get('/profile/detail/')
        self.assertEqual(response.status_code, 302)
        
    def test_profile_detail_view_with_login(self):
        """user authenticated should access
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/profile/detail/')
        self.assertEqual(response.status_code, 200)
        
    def test_profile_detail_view_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:profile_detail'))
        self.assertEqual(response.status_code, 200)
        
    def test_profile_detail_view_template_correct(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:profile_detail'))
        self.assertTemplateUsed(response, 'blog/profile/profile.html')
        
    def test_profile_detail_view(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:profile_detail'))
        self.assertContains(response, 'test')
        self.assertContains(response, 'test@example.com')
        
    # ------------ Profile Update View ---------------
    def test_profile_update_view_without_login(self):
        """user not authenticated should not access
        and redirect to login page
        """
        response = self.client.get('/profile/update/')
        self.assertEqual(response.status_code, 302)
        
    def test_profile_update_view_with_login(self):
        """user authenticated should access
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/profile/update/')
        self.assertEqual(response.status_code, 200)
        
    def test_profile_update_view_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:profile_update'))
        self.assertEqual(response.status_code, 200)
        
    def test_profile_update_view_template_correct(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('blog:profile_update'))
        self.assertTemplateUsed(response, 'blog/profile/profile_update.html')
        
    def test_profile_update_view(self):
        self.client.login(username='test', password='test1234')
        response = self.client.post(path=reverse('blog:profile_update'),
            data={
                'username':'test',
                'email':'test@example.com',
                'first_name':'first',
                'last_name':'last',
                'age':15,
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.last().username, 'test')
        self.assertEqual(get_user_model().objects.last().age, 15)
        self.assertEqual(get_user_model().objects.last().first_name, 'first')

    # --------- Author Information View ---------
    def test_author_information_url(self):
        response = self.client.get('/author/test/')
        self.assertEqual(response.status_code, 200)

    def test_author_information_url_name(self):
        response = self.client.get(
            reverse('blog:author_detail', kwargs={'username': 'test'}))
        self.assertEqual(response.status_code, 200)

    def test_author_information_template_correct(self):
        response = self.client.get(
            reverse('blog:author_detail', kwargs={'username': 'test'}))
        self.assertTemplateUsed(response, 'blog/author.html')

    def test_author_information_view(self):
        response = self.client.get(
            reverse('blog:author_detail', kwargs={'username': 'test'}))
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.article.title)
        self.assertNotContains(response, self.article_2.title)
    
    # --------- Article PreView View ----------
    def test_article_preview_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/first/preview/')
        self.assertEqual(response.status_code, 302)
        
    def test_article_preview_with_login_without_owner(self):
        """User is authenticated but user is not owner
        should not access the page
        """
        # login with user_2 and article is First
        self.client.login(username='test2', password='test12345')
        response = self.client.get('/panel/first/preview/')
        self.assertEqual(response.status_code, 404)
        
    def test_article_preview_with_login_with_owner(self):
        """User is authenticated and user is owner
        should access the page
        """
        # login with user and article is First
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/first/preview/')
        self.assertEqual(response.status_code, 200)
        
    def test_article_preview_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/panel/first/preview/')
        self.assertEqual(response.status_code, 200)

    def test_article_preview_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('blog:article_preview', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_article_preview_template_correct(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('blog:article_preview', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'admin_panel/preview.html')

    def test_article_preview_get_request(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('blog:article_preview', kwargs={'slug': 'first'}))
        self.assertContains(response, 'First')

    # --------- Share Post View ----------
    def test_share_post_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/first/share/')
        self.assertEqual(response.status_code, 302)

    def test_share_post_with_login(self):
        """User is authenticated should access the page
        """
        self.client.login(username='test', password='test1234')
        response = self.client.get('/first/share/')
        self.assertEqual(response.status_code, 200)

    def test_share_post_url(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get('/first/share/')
        self.assertEqual(response.status_code, 200)

    def test_share_post_url_name(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('blog:share_article', kwargs={'slug': 'first'}))
        self.assertEqual(response.status_code, 200)

    def test_share_post_template_correct(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(
            reverse('blog:share_article', kwargs={'slug': 'first'}))
        self.assertTemplateUsed(response, 'blog/share_post.html')

    def test_share_post_request_post(self):
        data = {
            'name': 'test_post',
            'email': 'test_post@gmail.com',
            'message': 'test-post message',
        }
        self.client.login(username='test', password='test1234')
        response = self.client.post(
            reverse('blog:share_article', kwargs={'slug': 'first'}), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/first/')


# ============== Test Category View ==============
class TestCategoryView(TestCase):

    def setUp(self):
        
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

        self.user = get_user_model().objects.create_user(
            username='test',
            password='1234',
            email='test@example.com'
        )

        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            position=1,
            status=True,
        )
        
        self.article = Blog.objects.create(
            title='First',
            slug='first',
            author=self.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='small_category_views_gif.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            view=1,
            code=10000,
            status=Blog.PUBLISH,
        )
        self.article.category.add(self.category)
        self.article.save()

    def tearDown(self):
        """Depopulate created model instances from test database."""
        for model in MODELS:
            for obj in model.objects.all():
                obj.delete()
                
    # --------- Create Category ---------
    def test_category_create_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/category/create/')
        self.assertEqual(response.status_code, 302)
        
    def test_category_create_with_login_without_author(self):
        """User is authenticated but is not author
        should not access the page
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/create/')
        self.assertEqual(response.status_code, 404)
        
    def test_category_create_with_login_with_author(self):
        """User is authenticated and is author
        should access the page
        """
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/create/')
        self.assertEqual(response.status_code, 200)
        
    def test_category_create_url(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/create/')
        self.assertEqual(response.status_code, 200)

    def test_category_create_url_name(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('blog:category_create'))
        self.assertEqual(response.status_code, 200)

    def test_category_create_template_correct(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('blog:category_create'))
        self.assertTemplateUsed(response, 'admin_panel/category_create.html')

    def test_category_create(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('blog:category_create'), data={
            'title': self.category.title,
            'slug': 'planet',
            'position': 2,
            'parent': '',
            'status': True,
        })
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.last().slug, 'planet')
        self.assertEqual(response.status_code, 302)
        
    # --------- Update Category ---------
    def test_category_update_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/category/update/test-category/')
        self.assertEqual(response.status_code, 302)

    def test_category_update_with_login_without_author(self):
        """User is authenticated but is not author
        should not access the page
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/update/test-category/')
        self.assertEqual(response.status_code, 404)

    def test_category_update_with_login_with_author(self):
        """User is authenticated and is author
        should access the page
        """
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/update/test-category/')
        self.assertEqual(response.status_code, 200)

    def test_category_update_url(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/update/test-category/')
        self.assertEqual(response.status_code, 200)

    def test_category_update_url_name(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('blog:category_update',kwargs={'slug':'test-category'}))
        self.assertEqual(response.status_code, 200)

    def test_category_update_template_correct(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(
            reverse('blog:category_update', kwargs={'slug': 'test-category'}))
        self.assertTemplateUsed(response, 'admin_panel/category_update.html')

    def test_category_update(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('blog:category_update', kwargs={'slug': 'test-category'}), data={
            'title': self.category.title,
            'slug': 'planet',
            'position': 2,
            'parent': '',
            'status': True,
        })
        self.category.refresh_from_db()
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().slug, 'planet')
        self.assertEqual(Category.objects.first().position, 2)
        self.assertEqual(response.status_code, 302)
    
    # --------- Delete Category ---------
    def test_category_delete_without_login(self):
        """User is not authenticated should not access the page
        """
        response = self.client.get('/panel/category/delete/test-category/')
        self.assertEqual(response.status_code, 302)
        
    def test_category_delete_with_login_without_superuser(self):
        """User is authenticated but is not superuser
        should not access the page
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/delete/test-category/')
        self.assertEqual(response.status_code, 404)
        
    def test_category_delete_with_login_with_superuser(self):
        """User is authenticated and is superuser
        should access the page
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/delete/test-category/')
        self.assertEqual(response.status_code, 200)
        
    def test_category_delete_url(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/panel/category/delete/test-category/')
        self.assertEqual(response.status_code, 200)

    def test_category_delete_url_name(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('blog:category_delete',kwargs={'slug':'test-category'}))
        self.assertEqual(response.status_code, 200)

    def test_category_delete_template_correct(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(
            reverse('blog:category_delete', kwargs={'slug': 'test-category'}))
        self.assertTemplateUsed(response, 'admin_panel/category_delete.html')

    def test_category_delete(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('blog:category_delete', kwargs={'slug': 'test-category'}), data={
            'slug': 'test-category',
        })
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(response.status_code, 302)
    
    # --------- Category Articles View ---------
    def test_category_articles_url(self):
        response = self.client.get('/category/test-category/')
        self.assertEqual(response.status_code, 200)

    def test_category_articles_url_name(self):
        response = self.client.get(
            reverse('blog:category_articles', kwargs={'slug':'test-category'}))
        self.assertEqual(response.status_code, 200)

    def test_category_articles_template_correct(self):
        response = self.client.get(
            reverse('blog:category_articles', kwargs={'slug':'test-category'}))
        self.assertTemplateUsed(response, 'blog/category_articles.html')

    def test_category_articles(self):
        response = self.client.get(
            reverse('blog:category_articles', kwargs={'slug':'test-category'}))
        self.assertContains(response, 'first')
        self.assertContains(response, 'Test Category')
        self.assertEqual(self.category.blog_set.count(), 1)
        self.assertEqual(self.category.blog_set.first().title, 'First')
