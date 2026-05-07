from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, ProductType, Transaction
from accounts.models import Profile

class MerchstoreCartTests(TestCase):
    def setUp(self):
        # Create users/profiles
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.profile1 = Profile.objects.create(user=self.user1, display_name='User One', role='Market Seller')
        
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.profile2 = Profile.objects.create(user=self.user2, display_name='User Two', role='Customer')
        
        # Create product type
        self.ptype = ProductType.objects.create(name='Electronics', description='Gadgets')
        
        # Create product
        self.product = Product.objects.create(
            name='Smartphone',
            product_type=self.ptype,
            owner=self.profile1,
            price=500.00,
            stock=10,
            status='Available'
        )
        
        self.client = Client()
        self.client.login(username='user2', password='password')

    def test_cart_checkout(self):
        # Add to cart
        transaction = Transaction.objects.create(
            buyer=self.profile2,
            product=self.product,
            amount=1,
            status='On cart'
        )
        
        # Check cart page
        response = self.client.get(reverse('merchstore:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'Checkout')
        
        # Perform checkout
        response = self.client.post(reverse('merchstore:cart'))
        self.assertRedirects(response, reverse('merchstore:transactions_list'))
        
        # Verify status update
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'To Pay')
        
    def test_transaction_list_shows_purchases(self):
        # Create a 'To Pay' transaction (already checked out)
        Transaction.objects.create(
            buyer=self.profile2,
            product=self.product,
            amount=1,
            status='To Pay'
        )
        
        response = self.client.get(reverse('merchstore:transactions_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Purchases')
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'To Pay')

    def test_full_flow(self):
        # 1. View product detail
        response = self.client.get(reverse('merchstore:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        
        # 2. Add to cart
        response = self.client.post(reverse('merchstore:product-detail', kwargs={'pk': self.product.pk}), {'amount': 2})
        self.assertRedirects(response, reverse('merchstore:cart'))
        
        # 3. View cart
        response = self.client.get(reverse('merchstore:cart'))
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, '2 units')
        
        # 4. Checkout
        response = self.client.post(reverse('merchstore:cart'))
        self.assertRedirects(response, reverse('merchstore:transactions_list'))
        
        # 5. View transaction list
        response = self.client.get(reverse('merchstore:transactions_list'))
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, '2 units')
        self.assertContains(response, 'To Pay')
