from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Register
from django.core.files.uploadedfile import SimpleUploadedFile

class ChickenAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a sample product with a dummy 1x1 GIF
        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
        image = SimpleUploadedFile("test_chicken.gif", tiny_gif, content_type="image/gif")
        self.product = Product.objects.create(
            name="Crispy Wings",
            price=199.00,
            discription="Delicious and crispy chicken wings",
            image=image
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crispy Wings")

    def test_profile_search(self):
        response = self.client.get(reverse('profile') + "?q=Wings")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crispy Wings")

        response_empty = self.client.get(reverse('profile') + "?q=NonExistentItem")
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Crispy Wings")

    def test_product_details_page(self):
        response = self.client.get(reverse('product_details', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crispy Wings")

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_and_login_flow(self):
        # Register
        reg_response = self.client.post(reverse('register'), {
            'username': 'harry',
            'email': 'harry@chicken.com',
            'password': 'password123'
        })
        self.assertEqual(reg_response.status_code, 302)
        self.assertTrue(Register.objects.filter(username='harry').exists())

        # Duplicate email registration test
        dup_response = self.client.post(reverse('register'), {
            'username': 'harry2',
            'email': 'harry@chicken.com',
            'password': 'password123'
        })
        self.assertEqual(dup_response.status_code, 200)
        self.assertContains(dup_response, "email already exist")

        # Login success
        login_response = self.client.post(reverse('login'), {
            'username': 'harry',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(self.client.session.get('username'), 'harry')

        # Login failure
        bad_login = self.client.post(reverse('login'), {
            'username': 'harry',
            'password': 'wrongpassword'
        })
        self.assertEqual(bad_login.status_code, 200)
        self.assertContains(bad_login, "invalid username or password")

    def test_cart_operations(self):
        # Add to cart
        add_response = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(add_response.status_code, 302)

        # Verify session
        session = self.client.session
        self.assertIn(str(self.product.id), session['cart'])
        self.assertEqual(session['cart'][str(self.product.id)], 1)

        # View cart
        cart_response = self.client.get(reverse('cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Crispy Wings")

        # Remove from cart
        rem_response = self.client.get(reverse('remove_cart', args=[self.product.id]))
        self.assertEqual(rem_response.status_code, 302)
        self.assertNotIn(str(self.product.id), self.client.session.get('cart', {}))
