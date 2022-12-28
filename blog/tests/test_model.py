from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Blog, Category, IpAddress

MODELS = [Blog, Category,]


# ============== Test IpAddress Model ===============
class TestIpAddressModel(TestCase):
    
    def setUp(self):
        self.ip_address_1 = IpAddress.objects.create(ip_address='127.0.0.1')
        self.ip_address_2 = IpAddress.objects.create(ip_address='127.0.0.2')

    def test_ip_address_model(self):
        self.assertTrue(isinstance(self.ip_address_1, IpAddress))
        self.assertTrue(isinstance(self.ip_address_2, IpAddress))
        self.assertEqual(self.ip_address_1.id, 1)
        self.assertEqual(self.ip_address_1.ip_address, '127.0.0.1')
        self.assertEqual(str(self.ip_address_1), '127.0.0.1')
        self.assertEqual(self.ip_address_2.id, 2)
        self.assertEqual(self.ip_address_2.ip_address, '127.0.0.2')
        self.assertEqual(str(self.ip_address_2), '127.0.0.2')
        self.assertEqual(IpAddress.objects.count(), 2)


# ============== Test Blog Model ===============
class TestBlogModel(TestCase):

    def setUp(self):
        # small black gif
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        
        self.ip_address = IpAddress.objects.create(ip_address='127.0.0.1')

        self.user = get_user_model().objects.create_user(
            username='test',
            password='1234',
            email='test@example.com'
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
            thumbnail=SimpleUploadedFile(name='small.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10000,
            view=1,
            status=Blog.PUBLISH,
        )
        self.article.category.add(self.category)
        self.article.hits.add(self.ip_address)
        self.article.save()
        
        self.article_2 = Blog.objects.create(
            title='Second',
            slug='second',
            author=self.user,
            content='second something',
            thumbnail=SimpleUploadedFile(name='second_small.gif',
                                         content=self.small_gif,
                                         content_type='image/gif',
                                         ),
            code=10001,
            view=5,
            status=Blog.DRAFT,
        )
        self.article_2.category.add(self.category)
        self.article_2.hits.add(self.ip_address)
        self.article_2.save()

    def tearDown(self):
        """Depopulate created model instances from test database."""
        for model in MODELS:
            for obj in model.objects.all():
                obj.delete()

    def test_blog_obj(self):
        self.assertTrue(isinstance(self.article, Blog))
        self.assertEqual(self.article.title, 'First')
        self.assertEqual(self.article.category.first().title, self.category.title)
        self.assertEqual(self.article.hits.first().ip_address, '127.0.0.1')
        self.assertEqual(self.article.slug, 'first')
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.content, 'something')
        self.assertEqual(
            self.article.thumbnail.url,
            '/media/images/small.gif'
        )
        self.assertEqual(self.article.code, 10000)
        self.assertEqual(self.article.view, 1)
        self.assertEqual(self.article.status, 'p')
        self.assertEqual(self.article.special, False)
        self.assertEqual(str(self.article), self.article.title)
        # test Blog custom manager
        self.assertEqual(
            Blog.objects.published().count(),           
            Blog.objects.filter(status='p').count()
        )
        self.assertEqual(Blog.objects.published().count(), 1)
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(self.article.get_absolute_url(), '/first/')
        
        

# ============== Test Category Model ===============
class TestCategoryModel(TestCase):
    
    def setUp(self):
        self.category = Category.objects.create(
            title='First',
            slug='first',
            position=1,
            status=True,
            parent=None,
        )
    
        self.category_2 = Category.objects.create(
            title='Second',
            slug='second',
            position=2,
            status=False,
            parent=None,
        )
    
    def test_category_model(self):
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(self.category.title, 'First')
        self.assertEqual(self.category.slug, 'first')
        self.assertEqual(self.category.position, 1)
        self.assertEqual(self.category.status, True)
        self.assertEqual(self.category.parent, None)
        self.assertEqual(str(self.category), 'First')
        # test Category custom manager
        self.assertEqual(                                 
            Category.objects.active().count(),
            Category.objects.filter(status=True).count()             
        )
        self.assertEqual(Category.objects.active().count(), 1)
        self.assertEqual(Category.objects.count(), 2)
        
