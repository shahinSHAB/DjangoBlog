from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import Blog, Category
from comments.models import Comment


class TestUserViewSetApi(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='test',
                                                        email='test@example.com',
                                                        password='test1234',
                                                        first_name='test1',
                                                        last_name='test2',
                                                        )
        cls.user_2 = get_user_model().objects.create_user(username='test2',
                                                        email='test2@example.com',
                                                        password='test21234',
                                                        first_name='test2',
                                                        last_name='test3',
                                                        )

    def test_users_list_api_without_login(self):
        """User is not authenticated and is not staff
        should not access api
        """
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_users_list_api_with_login_without_staff_user(self):
        """User is authenticated but is not staff
        should not access api
        """
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_users_list_api_with_login_with_staff_user(self):
        """User is authenticated and is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_list_api(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertContains(response, self.user)
        self.assertContains(response, self.user_2)
    
    def test_users_detail_api_without_login(self):
        """User is not authenticated should not access api
        """
        response = self.client.get('/api/v1/users/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_detail_api_with_login_without_staff_user(self):
        """User is authenticated but is not staff should not access api
        """
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_users_detail_api_with_login_with_staff_user_no_owner(self):
        """User is authenticated and is staff but not owner of object
        should not access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/2/')   # because self.user is not owner of this obj
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_users_detail_api_with_login_with_staff_user_owner(self):
        """User is authenticated and is staff and owner of object
        and method is in safe '(GET,HEAD,OPTIONS)' should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/1/')   # because self.user is owner of this obj
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_detail_api(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test',
                          email='test@example.com',
                          password='test1234',
                          )
        response = self.client.get('/api/v1/users/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset({
            'username':'test',
            'id':1,
            'email':'test@example.com',
            'first_name':'test1',
            'last_name':'test2',
        }, response.data)


# ================ Test blog api views =================
class TestBlogApiViews(APITestCase):
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
            status=True,
        )

        cls.article = Blog.objects.create(
            title='First',
            slug='first',
            author=cls.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='first_small_api.gif',
                                         content=cls.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10000,
            view=1,
            status=Blog.PUBLISH,
        )
        cls.article.category.add(cls.category)
        cls.article.save()

        cls.article_2 = Blog.objects.create(
            title='Second',
            slug='second',
            author=cls.user,
            content='second something',
            thumbnail=SimpleUploadedFile(name='second_small_api.gif',
                                         content=cls.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10001,
            view=5,
            status=Blog.DRAFT,
        )
        cls.article_2.category.add(cls.category)
        cls.article_2.save()
        
        cls.article_3 = Blog.objects.create(
            title='Third',
            slug='third',
            author=cls.user,
            content='third something',
            thumbnail=SimpleUploadedFile(name='third_small_api.gif',
                                         content=cls.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10005,
            view=3,
            publish=timezone.now() - timedelta(days=15),
            status=Blog.PUBLISH,
        )
        cls.article_3.category.add(cls.category)
        cls.article_3.save()
    
    # ---------- test article list api view ----------
    def test_can_not_access_article_list_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_access_article_list_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_article_list_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:published_articles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_list_api_view_without_search_query(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles/')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Second')         # because this article was not published
        self.assertEqual(len(response.data), 2)           
        self.assertNotEqual(len(response.data), 3)           
    
    def test_article_list_api_view_with_correct_search_query(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles/?q=first')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Second')         
        self.assertEqual(len(response.data), 1)           
        self.assertEqual(response.status_code, status.HTTP_200_OK)           
        self.assertNotEqual(len(response.data), 2)           
    
    def test_article_list_api_view_with_not_correct_search_query(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles/?q=new')           
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)          
    
    # ---------- test article detail api view ----------
    def test_can_not_access_article_detail_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_article_detail_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles/first/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:article_detail', kwargs={'slug':'first'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:article_detail', kwargs={'slug':'first'}))
        self.assertDictContainsSubset({
            'title':'First',
            'slug':'first',
            'author':'test',
            'content':'something',
            'code':10000,
            'view':1,
            'status':'p',
            'thumbnail':'/media/images/first_small_api.gif',
            'category':['Test Category'],
        }, response.data)

    # ---------- test all-articles api view ----------
    def test_can_not_access_all_articles_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/admin-panel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_all_articles_with_staff_user_api_view(self):
        """User is superuser or user is authenticated and 
        user is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/admin-panel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_access_all_articles_without_staff_user_api_view(self):
        """User is not superuser or user is not authenticated and 
        user is not staff should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/admin-panel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_articles_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:all_articles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_all_articles_api_view(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:all_articles'))
        self.assertEqual(len(response.data), 3)
        self.assertContains(response, 'First')        
        self.assertContains(response, 'Second')
    
    # ---------- test article-detail-update-delete api view ----------
    def test_can_not_access_article_detail_update_delete_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/admin-panel/detail/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_article_detail_update_delete_with_owner_and_draft_status_api_view(self):
        """User is authenticated and user is superuser or user is authenticated
        and user is author and owner of article and article has 'draft' or 'back'
        status should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/admin-panel/detail/second/')  # article "second" is in draft status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_access_article_detail_update_delete_with_owner_and_no_draft_status_api_view(self):
        """User is authenticated and user is author and owner of article but
        article has not 'draft' or 'back' status should  not access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/admin-panel/detail/first/')  # article "first" is not in draft status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_detail_update_delete_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:update_delete_article', kwargs={'slug':'second'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # ----- test article detail ---------
    def test_article_just_detail_api_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:update_delete_article', kwargs={'slug':'first'}))
        self.assertDictContainsSubset({
            'title':'First',
            'slug':'first',
            'author':'test',
            'content':'something',
            'code':10000,
            'view':1,
            'status':'p',
            'thumbnail':'/media/images/first_small_api.gif',
            'category':['Test Category'],
        }, response.data)
        
    # ----- test article update ---------
    def test_article_just_update_api_view(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.put(
            path=reverse('api:update_delete_article', kwargs={'slug': 'first'}),
            data={
                'id':1,
                'title':'First Updated',
                'slug':'first-updated',
                'author':'test',
                'content':'something',
                'code':10000,
                'view':1,
                'special':False,
                'publish':'2022-10-03T16:14:43+03:30',
                'status':'p',
                'thumbnail':'/media/images/first_small_api.gif',
                'category':['Test Category'],
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(Blog.objects.last().title, 'First Updated')
        self.assertEqual(Blog.objects.last().slug, 'first-updated')

    # ----- test article delete ---------
    def test_article_just_delete_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        self.assertEqual(Blog.objects.count(), 3)
        response = self.client.delete(
            path=reverse('api:update_delete_article', kwargs={'slug':'second'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Blog.objects.count(), 2)
        
    # ---------- test articles period api view ----------
    # test last-month
    def test_can_not_access_articles_period_last_month_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-period/last-month/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_articles_period_last_month_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-month/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_month_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:articles_period', kwargs={'slug':'last-month'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_month_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-month/')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Third')
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 2)
        self.assertNotEqual(len(response.data), 3)

    # test last-week
    def test_can_not_access_articles_period_last_week_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-period/last-week/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_articles_period_last_week_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-week/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_week_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:articles_period', kwargs={'slug':'last-week'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_week_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-week/')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Third')     # because this article is older than a week
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(len(response.data), 2)

    # test last-day
    def test_can_not_access_articles_period_last_day_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-period/last-day/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_articles_period_last_day_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-day/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_day_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:articles_period', kwargs={'slug':'last-day'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_day_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-day/')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Third')     # because this article is older than a day
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(len(response.data), 2)

    # test last-five_articles
    def test_can_not_access_articles_period_last_five_articles_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-period/last-five-articles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_articles_period_last_five_articles_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-five-articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_five_articles_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:articles_period', kwargs={'slug':'last-five-articles'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_articles_period_last_five_articles_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-five-articles/')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Third')        
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 2)
        self.assertNotEqual(len(response.data), 3)

    # -------- test articles period not correct url ------------
    def test_articles_period_not_correct_url(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-period/last-wrong-slug/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------- test most viewed articles api view ----------
    # test last-month most-view
    def test_can_not_access_most_viewed_articles_last_month_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-most-view/last-month/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_most_viewed_articles_last_month_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-month/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_month_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:most_viewed_articles', kwargs={'slug':'last-month'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_month_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-month/')
        self.assertEqual(response.data[0]['title'], 'Third')   # because of view ordering
        self.assertEqual(response.data[1]['title'], 'First')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Third')
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 2)
        self.assertNotEqual(len(response.data), 3)

    # test last-week most-view
    def test_can_not_access_most_viewed_articles_last_week_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-most-view/last-week/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_most_viewed_articles_last_week_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-week/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_week_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:most_viewed_articles', kwargs={'slug':'last-week'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_week_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-week/')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Third')     # because this article is older than a week
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(len(response.data), 2)

    # test last-day most-view
    def test_can_not_access_most_viewed_articles_last_day_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-most-view/last-day/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_most_viewed_articles_last_day_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-day/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_day_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:most_viewed_articles', kwargs={'slug':'last-day'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_day_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-day/')
        self.assertContains(response, 'First')
        self.assertNotContains(response, 'Third')     # because this article is older than a day
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(len(response.data), 2)

    # test last-five_articles most-view
    def test_can_not_access_most_viewed_articles_last_five_articles_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/articles-most-view/last-five-articles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_most_viewed_articles_last_five_articles_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-five-articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_five_articles_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:most_viewed_articles', kwargs={'slug':'last-five-articles'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_most_viewed_articles_last_five_articles_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-five-articles/')
        self.assertEqual(response.data[0]['title'], 'Third')   # because of view ordering
        self.assertEqual(response.data[1]['title'], 'First')
        self.assertContains(response, 'First')
        self.assertContains(response, 'Third')        
        self.assertNotContains(response, 'Second')    # because this article was not published
        self.assertEqual(len(response.data), 2)
        self.assertNotEqual(len(response.data), 3)

    # ----- test most viewed articles not correct url -----
    def test_most_viewed_articles_not_correct_url(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/articles-most-view/last-wrong-slug/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------ test profile detail api view -------------
    def test_profile_detail_api_view_without_login(self):
        """user not authenticated should not access
        """
        response = self.client.get('/api/v1/profile/detail/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_profile_detail_api_view_with_login(self):
        """user authenticated should access url
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/profile/detail/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_detail_api_view_url_name(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:profile_detail', kwargs={'username':'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_detail_api_view(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:profile_detail', kwargs={'username':'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['id'], 1)
        
    # ------------ test profile detail api view -------------
    def test_profile_update_api_view_without_login(self):
        """user not authenticated should not access
        """
        response = self.client.get('/api/v1/profile/update/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_profile_update_api_view_with_login(self):
        """user authenticated should access url
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/profile/update/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_update_api_view_url_name(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:profile_update', kwargs={'username':'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_profile_update_api_view(self):
        self.client.login(username='test', password='1234')
        response = self.client.put(
            reverse('api:profile_update', kwargs={'username':'test'}),
            data={
                "username": "test",
                "email": "test@example.com",
                "first_name": "name",
                "last_name": "last",
                "phone": "00-000-0000",
                "age": 27,
                "gender": "m",
            },                            
        )                                                    
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)                           
        self.assertEqual(get_user_model().objects.first().first_name, 'name')                           
        self.assertEqual(get_user_model().objects.first().last_name, 'last')                           
        self.assertEqual(get_user_model().objects.first().gender, 'm')                           
        self.assertEqual(get_user_model().objects.first().phone, '00-000-0000')                           
    
    # ------------ test author information api view -----------
    def test_author_information_api_view_without_login(self):
        """user not authenticated should not access
        """
        response = self.client.get('/api/v1/author/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_information_api_view_with_login(self):
        """user authenticated should access url
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/author/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_information_api_view_url_name(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(
            reverse('api:author_information', kwargs={'username': 'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_information_api_view(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(
            reverse('api:author_information', kwargs={'username': 'test'}))
        self.assertContains(response, 'First')
        self.assertContains(response, 'Third')
        self.assertNotContains(response, 'Second')      # because this article is draft
        self.assertEqual(len(response.data), 2)

    # ----------- test Share Post api view -----------
    def test_share_post_api_view_without_login(self):
        response = self.client.get('/api/v1/articles/first/share/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_share_post_api_view_with_login(self):
        """User is is not authenticated should access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/articles/first/share/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_post_api_view_url_name(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:share_article', kwargs={'slug':'first'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_post_api_view_get_request(self):
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:share_article', kwargs={'slug':'first'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'First')
        self.assertEqual(response.data['slug'], 'first')
        self.assertEqual(response.data['view'], 1)
        self.assertEqual(response.data['author'], 'test')  # author indicate user's name

    def test_share_post_api_view_post_request(self):
        data = {
            'name': 'test_post',
            'email': 'test_post@gmail.com',
            'message': 'test_post message',
        }
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('api:share_article', kwargs={'slug':'first'}),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'post shared successfully')

    def test_share_post_api_view_post_request_without_name_and_message(self):
        data = {
            'email': 'test_post@gmail.com',
        }
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('api:share_article', kwargs={'slug':'first'}),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'post shared successfully')

    def test_share_post_api_view_post_request_without_email(self):
        data = {
            'name': 'test_post',
            'message': 'test_post message',
        }
        self.client.login(username='test', password='1234')
        response = self.client.post(reverse('api:share_article', kwargs={'slug':'first'}),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# ================ Test category api views =================
class TestCategoryApiViews(APITestCase):
    
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
            title='Category',
            slug='test',
            position=1,
            status=True,
            parent=None,
        )
        
        self.article = Blog.objects.create(
            title='First',
            slug='first',
            author=self.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='first_category_small_api.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10000,
            view=1,
            status=Blog.PUBLISH,
        )
        self.article.category.add(self.category)
        self.article.save()
        
    # ---------- test category-detail-update-delete api view ----------
    def test_can_not_access_category_detail_update_delete_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get(
            '/api/v1/admin-panel/category/detail/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_category_detail_update_delete_with_author_user_api_view(self):
        """User is authenticated and is superuser or is authenticated and
        is author then user should access api
        """
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(
            '/api/v1/admin-panel/category/detail/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_access_category_detail_update_delete_without_author_user_api_view(self):
        """User is authenticated and is superuser or is authenticated and
        is author then user should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(
            '/api/v1/admin-panel/category/detail/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail_update_delete_api_view_url_name(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(
            reverse('api:update_delete_category', kwargs={'slug': 'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # ----- test category detail ---------
    def test_category_detail_api_view(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(
            reverse('api:update_delete_category', kwargs={'slug': 'test'}))
        self.assertDictContainsSubset({
            'title': 'Category',
            'slug': 'test',
            'position': 1,
            'parent': None,
            'status': True,
        }, response.data)
        
    # ----- test category update ---------
    def test_category_update_api_view(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.put(
            path=reverse('api:update_delete_category',kwargs={'slug': 'test'}),
            data={
                'title': 'Category Updated',
                'slug': 'test_updated',
                'parent':'',
                'position':2,
                'status':True,
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(Category.objects.first().title, 'Category Updated')
        self.assertEqual(Category.objects.first().slug, 'test_updated')
        self.assertEqual(Category.objects.first().position, 2)
        
    # ----- test category delete ---------
    def test_category_delete_api_view(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        self.assertEqual(Category.objects.count(), 1)
        response = self.client.delete(
            path=reverse('api:update_delete_category', kwargs={'slug':'test'}))
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
        
    # ---------- test CreateCategory Api View ----------
    def test_create_category_api_view(self):
        self.user.is_author = True
        self.user.save()
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        self.assertEqual(Category.objects.count(), 1)
        response = self.client.post(path=reverse('api:category_create'), data={
            'title':'New',
            'slug':'new',
            'parent':[1],
            'position':3,
            'status':True,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.last().title, 'New')
        
    # ---------- test category articles api view ----------
    def test_can_not_access_category_articles_api_view(self):
        """User not authenticated should not access api
        """
        response = self.client.get('/api/v1/category/test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_category_articles_api_view(self):
        """User authenticated should access api
        """
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/category/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_articles_api_view_url_name(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get(reverse('api:category_articles', kwargs={'slug':'test'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_articles_api_view(self):
        self.client.login(
            username='test',
            password='1234',
            email='test@example.com',
        )
        response = self.client.get('/api/v1/category/test/')
        self.assertContains(response, 'First')
        self.assertContains(response, 'something')
        self.assertNotContains(response, 'New Title')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.category.blog_set.first().title, 'First')
        

# ============= Test Comments Api Views ==============
class TestCommentsApiViews(APITestCase):
    
    def setUp(self):

        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )

        self.user = get_user_model().objects.create_user(
            username='test',
            password='1234',
            email='test@example.com',
            is_author = True
        )

        self.category = Category.objects.create(
            title='Category',
            slug='test',
            position=1,
            status=True,
            parent=None,
        )

        self.article = Blog.objects.create(
            title='First',
            slug='first',
            author=self.user,
            content='something',
            thumbnail=SimpleUploadedFile(name='first_comments_small_api.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10000,
            view=1,
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
            agree=12,
            disagree=5
        )
        self.comment_1 = Comment.objects.create(
            name='person_1',
            text='text_1',
            author=self.user,
            article=self.article,
            status=False,
            publish=timezone.now(),
            reply=None,
            agree=3,
            disagree=0
        )
        
    # ----------- test article comments api view -----------
    def test_article_comments_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_article_comments_api_view_with_login_without_staff_user(self):
        """User is not authenticated and is not superuser or user
        is not authenticated and is not staff then user should not access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_article_comments_api_view_with_login_with_staff_user(self):
        """User is authenticated and is superuser or user
        is authenticated and is staff then user should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_article_comments_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:article_comments', kwargs={'slug':'first'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_article_comments_api_view(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:article_comments', kwargs={'slug':'first'}))
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data), Comment.objects.count())
        self.assertContains(response, self.comment.name)
        self.assertContains(response, self.comment_1.name)
        
    # ----------- test published comments api view -----------
    def test_published_comments_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/published/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_published_comments_api_view_with_login_without_staff_user(self):
        """User is not authenticated and is not superuser or user is not
        authenticated and is not staff should not access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/published/first/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_published_comments_api_view_with_login_with_staff_user(self):
        """User is authenticated and is superuser or user is
        authenticated and is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/published/first/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_published_comments_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:published_comments', kwargs={'slug':'first'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_published_comments_api_view(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:published_comments', kwargs={'slug':'first'}))
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(len(response.data), Comment.objects.count())  # because comment_1 not published
        self.assertContains(response, self.comment.name)
        self.assertNotContains(response, self.comment_1.name)    # because comment_1 not published
        
    # ----------- test comment detail api view -----------
    def test_comment_detail_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/first/1/detail/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_detail_api_view_with_login_without_staff_user(self):
        """User is not authenticated and is not superuser or user is not
        authenticated and is not staff should not access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/detail/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_detail_api_view_with_login_with_staff_user(self):
        """User is authenticated and is superuser or user is
        authenticated and is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/detail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_detail_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:comment_detail', kwargs={'slug':'first', 'pk':1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_detail_with_staff_user_api_view(self):
        """User is superuser or user is authenticated and
        is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:comment_detail', kwargs={'slug':'first', 'pk':1}))
        self.assertEqual(response.data['name'], self.comment.name)
        self.assertEqual(response.data['text'], self.comment.text)
        self.assertEqual(response.data['agree'], self.comment.agree)
        self.assertEqual(response.data['disagree'], self.comment.disagree)
        self.assertEqual(response.data['author'], 1)   # equal to author id
        self.assertEqual(response.data['article'], 1)   # equal to article id
        
    # ----------- test comment create api view -----------
    def test_comment_create_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/first/create/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_create_api_view_with_login(self):
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/create/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_comment_create_api_view(self):
        self.client.login(username='test', password='1234')
        response = self.client.post(
            reverse('api:comment_create', kwargs={'slug':'first'}),
            data={
                'name':'person_2',
                'text':'text_2',
                'author': 1,
                'article':1,
                'status':True,
                'reply':'',
                'agree':7,
                'disagree':15,
                'publish': '2022-11-04 12:32:43',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Comment.objects.first().name, 'person_2')
        self.assertEqual(Comment.objects.first().text, 'text_2')

    # ----------- test comment update api view -----------
    def test_comment_update_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/first/1/update/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_update_api_view_with_login_without_staff_user(self):
        """User is not authenticated and is not superuser or user is not
        authenticated and is not staff should not access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/update/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_update_api_view_with_login_with_staff_user(self):
        """User is authenticated and is superuser or user is
        authenticated and is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/update/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_update_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:comment_update', kwargs={'slug':'first', 'pk':1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_update_api_view(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.put(
            reverse('api:comment_update', kwargs={'slug':'first', 'pk':1}),
            data={
                'name':'person_updated',
                'text':'text_updated',
                'author':1,
                'article':1,
                'status':True,
                'reply':''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().name, 'person_updated')
        self.assertEqual(Comment.objects.last().text, 'text_updated')
        self.assertEqual(Comment.objects.last().agree, 12)
        self.assertEqual(Comment.objects.last().disagree, 5)
        
        
    # ----------- test comment delete api view -----------
    def test_comment_delete_api_view_without_login(self):
        response = self.client.get('/api/v1/comments/first/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_delete_api_view_with_login_without_staff_user(self):
        """User is not authenticated and is not superuser or user is not
        authenticated and is not staff should not access api
        """
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_comment_delete_api_view_with_login_with_staff_user(self):
        """User is authenticated and is superuser or user is
        authenticated and is staff should access api
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get('/api/v1/comments/first/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_delete_api_view_url_name(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.get(reverse('api:comment_delete', kwargs={'slug':'first', 'pk':1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_comment_delete_api_view(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='test', password='1234')
        response = self.client.delete(reverse('api:comment_delete', kwargs={'slug':'first', 'pk':1}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)

