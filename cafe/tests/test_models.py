from django.test import TestCase
from ..models import *

class ServingTimeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        ServingTime.objects.create(time='morning')
       

    def test_time_max_length(self):
        serving_time = ServingTime.objects.get(id=1)
        max_length = serving_time._meta.get_field('time').max_length
        self.assertEquals(max_length, 7)

    def test_time_field_label(self):
        serving_time = ServingTime.objects.get(id=1)
        field_label = serving_time._meta.get_field('time').verbose_name
        self.assertEquals(field_label, 'time')
    
    def tearDown(self):
        ServingTime.objects.all().delete()

    
class CategoryMenuModelTest(TestCase):

    @classmethod
    def setUpTestData(cls) :
        serv1=ServingTime.objects.create(time='morning')
        sev2=ServingTime.objects.create(time='noon')

        CategoryMenu.objects.create(title='milk',serving_time =1)
        CategoryMenu.objects.get(id=1).serving_time.add(serv1,sev2)

    def test_title_field_label(self):
        Category_menu_obj=CategoryMenu.objects.get(id=1)
        field_lable=Category_menu_obj._meta.get_field("title").verbose_name
        self.assertEqual(field_lable,"title")

    def test_serving_time_field_label(self):
        Category_menu_obj=CategoryMenu.objects.get(id=1)
        field_lable=Category_menu_obj._meta.get_field("serving_time").verbose_name
        self.assertEqual(field_lable," serving_time ")

    def test_title_max_length(self):
        Category_menu_obj=CategoryMenu.objects.get(id=1)
        max_length=Category_menu_obj._meta.get_field("title")
        self.assertEqual(max_length,50)

    def test_serving_time_added(self):
        Category_menu_obj=CategoryMenu.objects.get(id=1)
        self.assertIn("noon",[serving_time.time for serving_time in Category_menu_obj.serving_time.all()])
        self.assertIn("morning",[serving_time.time for serving_time in Category_menu_obj.serving_time.all()])

    
    
class ItemsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        category_menu = CategoryMenu.objects.create(title='Test Category 1')
        user1 = CustomUser.objects.create(phonenumber='09157895420', email='user1@test.com')
        user2 = CustomUser.objects.create(phonenumber='09157842536', email='user2@test.com')
        item1=Items.objects.create(category_id=category_menu, title='Test Item', price=10.99, description='Test description', status=True)
        Like.objects.create(user=user1,item=item1)
        Like.objects.create(user=user2,item=item1)
       
        

    def test_title_max_length(self):
        item = Items.objects.get(title='Test Item')
        max_length = item._meta.get_field('title').max_length
        self.assertEquals(max_length, 100)

    def test_price_max_digits(self):
        item = Items.objects.get(title='Test Item')
        max_digits = item._meta.get_field('price').max_digits
        self.assertEquals(max_digits, 7)

    def test_description_max_length(self):
        item = Items.objects.get(title='Test Item')
        max_length = item._meta.get_field('description').max_length
        self.assertEquals(max_length, 255)

    def test_category_menu_relationship(self):
        item = Items.objects.get(title='Test Item')
        category_title = item.category_id.title
        self.assertEquals(category_title, 'Test Category 1')

    def test_like_relationship(self):
        item = Items.objects.get(title='Test Item')
        like_users_count = item.like.count()
        self.assertEquals(like_users_count, 2)
        self.assertIn("user1@test.com",[like.user.email for like in item.like.all()])
        self.assertIn("user2@test.com",[like.user.email for like in item.like.all()])

    def test_discount_value(self):
        item = Items.objects.get(title='Test Item')
        self.assertEquals(item.discount, 0)
        item.discount = 1
        self.assertEquals(item.discount, 1)

    

   
        