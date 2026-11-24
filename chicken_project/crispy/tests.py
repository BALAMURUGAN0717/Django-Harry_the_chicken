import os
import shutil
import tempfile
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Product, Register

# Temporary directory for media during test runs so production media is never polluted
TEST_MEDIA_DIR = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ChickenAppTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        # Clean product table so test fixtures are authoritative
        Product.objects.all().delete()
        # Create a sample image
        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
        image = SimpleUploadedFile("test_chicken.gif", tiny_gif, content_type="image/gif")
        
        self.product = Product.objects.create(
            name="Crispy Wings",
            price=Decimal("199.00"),
            discription="Delicious and crispy chicken wings",
            image=image,
            category="Crunchy"
        )
        self.lollipop = Product.objects.create(
            name="Chicken Lollipop",
            price=Decimal("199.00"),
            discription="Crunchy chicken lollipop with spicy dip",
            image=image,
            category="Chicken Meal"
        )
        self.tandoori = Product.objects.create(
            name="Chicken Tandoori",
            price=Decimal("249.00"),
            discription="Authentic smoky chicken tandoori",
            image=image,
            category="Grilled Chicken"
        )
        self.grill = Product.objects.create(
            name="Grill Tandoori",
            price=Decimal("299.00"),
            discription="Charred grill tandoori with spicy masala",
            image=image,
            category="Grilled Chicken"
        )
        self.popcorn = Product.objects.create(
            name="Fried Popcorn",
            price=Decimal("149.00"),
            discription="Crispy chicken popcorn snacks",
            image=image,
            category="Popcorn"
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('menu_products', response.context)
        self.assertIn('lollipop_id', response.context)
        self.assertIn('tandoori_id', response.context)
        self.assertIn('grill_id', response.context)
        self.assertEqual(response.context['lollipop_id'], self.lollipop.id)
        self.assertEqual(response.context['tandoori_id'], self.tandoori.id)
        self.assertEqual(response.context['grill_id'], self.grill.id)

    def test_read_more_links_on_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"/product_details/{self.lollipop.id}/")
        self.assertContains(response, f"/product_details/{self.tandoori.id}/")
        self.assertContains(response, f"/product_details/{self.grill.id}/")

    def test_special_menu_categories_present(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chicken Meal")
        self.assertContains(response, "Crunchy")
        self.assertContains(response, "Grilled Chicken")
        self.assertContains(response, "Popcorn")
        self.assertContains(response, f'data-category="{self.lollipop.category}"')
        self.assertContains(response, f'data-category="{self.product.category}"')
        self.assertContains(response, f'data-category="{self.tandoori.category}"')
        self.assertContains(response, f'data-category="{self.popcorn.category}"')

    def test_profile_page_and_category_filter(self):
        response_all = self.client.get(reverse('profile'))
        self.assertEqual(response_all.status_code, 200)
        self.assertContains(response_all, "Crispy Wings")
        self.assertContains(response_all, "Fried Popcorn")

        response_cat = self.client.get(reverse('profile') + "?category=Popcorn")
        self.assertEqual(response_cat.status_code, 200)
        self.assertContains(response_cat, "Fried Popcorn")
        self.assertNotContains(response_cat, "Crispy Wings")

    def test_product_details_page(self):
        response = self.client.get(reverse('product_details', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crispy Wings")
        self.assertContains(response, f"/add-to-cart/{self.product.id}/")

    def test_ajax_add_to_cart(self):
        response = self.client.get(
            reverse('add_to_cart', args=[self.product.id]),
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['cart_count'], 1)
        self.assertEqual(json_data['product_id'], self.product.id)

        # Add again to test quantity increment
        response2 = self.client.get(
            reverse('add_to_cart', args=[self.product.id]),
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json()['cart_count'], 2)

    def test_decrease_cart(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 2)

        dec_resp = self.client.get(reverse('decrease_cart', args=[self.product.id]))
        self.assertEqual(dec_resp.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 1)

        self.client.get(reverse('decrease_cart', args=[self.product.id]))
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get('cart', {}))

    def test_cart_operations(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.client.get(reverse('add_to_cart', args=[self.lollipop.id]))

        cart_response = self.client.get(reverse('cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Crispy Wings")
        self.assertContains(cart_response, "Chicken Lollipop")
        self.assertContains(cart_response, "398")

        rem_response = self.client.get(reverse('remove_cart', args=[self.product.id]))
        self.assertEqual(rem_response.status_code, 302)
        self.assertNotIn(str(self.product.id), self.client.session.get('cart', {}))

    def test_auth_register_and_login(self):
        # Register new user
        reg_resp = self.client.post(reverse('register'), {
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'password123'
        })
        self.assertEqual(reg_resp.status_code, 302)
        self.assertTrue(Register.objects.filter(username='tester').exists())

        # Duplicate register should fail
        reg_dup = self.client.post(reverse('register'), {
            'username': 'tester',
            'email': 'tester2@example.com',
            'password': 'password123'
        })
        self.assertEqual(reg_dup.status_code, 200)
        self.assertContains(reg_dup, "Username already exists")

        # Login with valid credentials
        login_resp = self.client.post(reverse('login'), {
            'username': 'tester',
            'password': 'password123'
        })
        self.assertEqual(login_resp.status_code, 302)
        self.assertEqual(self.client.session.get('username'), 'tester')

        # Check navbar shows username and logout link
        home_resp = self.client.get(reverse('home'))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, "tester")
        self.assertContains(home_resp, "/logout/")

        # Logout
        logout_resp = self.client.get(reverse('logout'))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertNotIn('username', self.client.session)
