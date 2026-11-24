from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Register
from django.core.files.uploadedfile import SimpleUploadedFile

class ChickenAppTests(TestCase):
    def setUp(self):
        self.client = Client()
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
            price=199.00,
            discription="Delicious and crispy chicken wings",
            image=image,
            category="Crunchy"
        )
        self.lollipop = Product.objects.create(
            name="Chicken Lollipop",
            price=199.00,
            discription="Crunchy chicken lollipop with spicy dip",
            image=image,
            category="Chicken Meal"
        )
        self.tandoori = Product.objects.create(
            name="Chicken Tandoori",
            price=249.00,
            discription="Authentic smoky chicken tandoori",
            image=image,
            category="Grilled Chicken"
        )
        self.grill = Product.objects.create(
            name="Grill Tandoori",
            price=299.00,
            discription="Charred grill tandoori with spicy masala",
            image=image,
            category="Grilled Chicken"
        )
        self.popcorn = Product.objects.create(
            name="Fried Popcorn",
            price=149.00,
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
        # Check that Read More links exist with correct URLs
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
        # Ensure products have data-category attributes
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
        # Add 2 items
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 2)

        # Decrease by 1
        dec_resp = self.client.get(reverse('decrease_cart', args=[self.product.id]))
        self.assertEqual(dec_resp.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 1)

        # Decrease again -> should be removed
        self.client.get(reverse('decrease_cart', args=[self.product.id]))
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get('cart', {}))

    def test_cart_operations(self):
        # Add to cart
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.client.get(reverse('add_to_cart', args=[self.lollipop.id]))

        # View cart
        cart_response = self.client.get(reverse('cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Crispy Wings")
        self.assertContains(cart_response, "Chicken Lollipop")
        # Total: 199.00 + 199.00 = 398.00
        self.assertContains(cart_response, "398")

        # Remove from cart
        rem_response = self.client.get(reverse('remove_cart', args=[self.product.id]))
        self.assertEqual(rem_response.status_code, 302)
        self.assertNotIn(str(self.product.id), self.client.session.get('cart', {}))
