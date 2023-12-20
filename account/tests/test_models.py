from django.test import TestCase
from account.models import *


class CustomUserTests(TestCase):
    fixtures = ['user.json']
    
    def setUp(self):
        """\________________[USER SETUP]________________/ """
        user1 = CustomUser.objects.get(email="arigatooo@gmail.com")
        user2 = CustomUser.objects.get(email="mamad@yahoo.com")
        
        """\________________[STAFF SETUP]________________/ """
        staff1 = Staff(user=user1, nationalcode="0092348321")
        staff1.save()
        
        """\________________[PERMISSION SETUP]________________/ """
        view_all_users_perm = Permission.objects.get(codename='view_all_users')
        edit_all_users_perm = Permission.objects.get(codename='edit_all_users')
        
        view_group = Group.objects.create(name='view_group')
        view_group.permissions.add(view_all_users_perm)
        view_group.save()
        
        edit_group = Group.objects.create(name='edit_group')
        edit_group.permissions.add(edit_all_users_perm)
        edit_group.save()

        user1.groups.add(view_group)
        user1.groups.add(edit_group)
        
        user2.groups.add(edit_group)
        
    """\______________________________[__STR__TEST]______________________________/"""
    
    def test_custom_user_str(self):
        jackichan = CustomUser.objects.get(firstname='Jacki', lastname='Chan')
        self.assertEqual(jackichan.__str__(), 'Jacki_Chan')

    def test_staff_str(self):
        staff1 = Staff.objects.get(nationalcode="0092348321")
        self.assertEqual(staff1.__str__(), 'Jacki Chan')
        
    """\____________________________[VERBOSE_NAME_TEST]____________________________/"""
    
    def test_phone_number_label(self):
        user1 = CustomUser.objects.get(id=1)
        user2 = CustomUser.objects.get(id=2)
        
        field_label1 = user1._meta.get_field('phonenumber').verbose_name
        field_label2 = user2._meta.get_field('phonenumber').verbose_name
        
        self.assertEqual(field_label1, 'Phone number')
        self.assertEqual(field_label2, 'Phone number')

    def test_email_label(self):
        user1 = CustomUser.objects.get(id=1)
        user2 = CustomUser.objects.get(id=2)
        
        field_label1 = user1._meta.get_field('email').verbose_name
        field_label2 = user2._meta.get_field('email').verbose_name
        
        self.assertEqual(field_label1, 'email address')
        self.assertEqual(field_label2, 'email address')
    
    """\_________________________________[ROLE_TEST]_______________________________/"""
                
    def test_has_perm(self):
        user1 = CustomUser.objects.get(email="arigatooo@gmail.com")
        user2 = CustomUser.objects.get(email="mamad@yahoo.com")
        
        view_all_users_perm = Permission.objects.get(codename='view_all_users')
        edit_all_users_perm = Permission.objects.get(codename='edit_all_users')
        
        self.assertTrue(user1.has_perm(view_all_users_perm))
        self.assertTrue(user1.has_perm(edit_all_users_perm))
        
        self.assertTrue(user2.has_perm(edit_all_users_perm))
        self.assertFalse(user2.has_perm(view_all_users_perm))
        
    def test_is_staff(self):
        user1 = CustomUser.objects.get(email="arigatooo@gmail.com")
        user2 = CustomUser.objects.get(email="mamad@yahoo.com")
        
        self.assertTrue(user1.is_staff)
        self.assertFalse(user2.is_staff)       
    
    
        
                