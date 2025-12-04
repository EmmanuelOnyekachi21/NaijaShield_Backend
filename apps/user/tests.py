"""
NaijaShield User App Tests
===========================

This file contains comprehensive tests for the User app functionality.
We'll cover:
1. Profile updates with location data
2. Profile completion calculation
3. Dashboard stats for different roles
4. User search (by role, location, name)
5. Trust badge creation and level calculation
6. Activity logging and retrieval

TESTING FUNDAMENTALS:
--------------------
Django tests use the TestCase class which:
- Creates a temporary test database
- Runs each test in a transaction (rolled back after test)
- Provides helper methods like self.client for API calls
- Uses assertions (self.assertEqual, self.assertTrue, etc.)

STRUCTURE:
---------
class TestClassName(TestCase):
    def setUp(self):
        # Runs before EACH test - create test data here
        
    def test_something(self):
        # Individual test case
        # Test name MUST start with "test_"
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from apps.user.models import TrustBadge, UserActivity

User = get_user_model()


class UserProfileUpdateTests(TestCase):
    """
    Test Profile Update Functionality
    
    LEARNING: setUp() runs before EACH test method
    This ensures each test starts with a clean slate
    """
    
    def setUp(self):
        """
        Create test users for each role
        
        LEARNING: We create users programmatically instead of using fixtures
        This makes tests more readable and maintainable
        """
        self.client = APIClient()
        
        # Create a farmer user
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='John',
            last_name='Farmer',
            role='farmer'
        )
        
        # Create a buyer user
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            phone_number='08087654321',
            password='testpass123',
            first_name='Jane',
            last_name='Buyer',
            role='buyer'
        )
        
        # Create a co-op user
        self.coop = User.objects.create_user(
            email='coop@test.com',
            phone_number='08011112222',
            password='testpass123',
            first_name='Coop',
            last_name='Leader',
            role='co-ops'
        )
    
    def test_profile_update_with_location_valid(self):
        """
        TEST 1: Valid profile update with location data
        
        LEARNING: 
        - self.client.force_authenticate() logs in the user
        - self.client.patch() makes a PATCH request
        - self.assertEqual() checks if two values are equal
        """
        # Authenticate as farmer
        self.client.force_authenticate(user=self.farmer)
        
        # Prepare update data with location
        data = {
            'location_lat': 6.5244,  # Lagos coordinates
            'location_lng': 3.3792,
            'location_text': 'Lagos, Nigeria',
            'bio': 'I grow organic vegetables'
        }
        
        # Make PATCH request to update profile
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        # Assert response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user from database
        self.farmer.refresh_from_db()
        
        # Assert location was saved correctly
        self.assertIsNotNone(self.farmer.location)
        self.assertEqual(self.farmer.location_text, 'Lagos, Nigeria')
        self.assertEqual(self.farmer.bio, 'I grow organic vegetables')
        
        # Assert location coordinates are correct (with tolerance for floating point)
        self.assertAlmostEqual(self.farmer.location.y, 6.5244, places=4)
        self.assertAlmostEqual(self.farmer.location.x, 3.3792, places=4)
    
    def test_profile_update_with_invalid_coordinates(self):
        """
        TEST 2: Invalid coordinates should return error
        
        LEARNING: Testing error cases is as important as testing success cases
        """
        self.client.force_authenticate(user=self.farmer)
        
        data = {
            'location_lat': 'invalid',  # Invalid latitude
            'location_lng': 3.3792,
        }
        
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_farmer_can_update_farm_size(self):
        """
        TEST 3: Farmers can update farm_size field
        
        LEARNING: Role-specific field validation
        """
        self.client.force_authenticate(user=self.farmer)
        
        data = {
            'farm_size': '5.5'  # 5.5 hectares
        }
        
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.farmer.refresh_from_db()
        self.assertEqual(self.farmer.farm_size, Decimal('5.5'))
    
    def test_buyer_cannot_update_farm_size(self):
        """
        TEST 4: Buyers should NOT be able to set farm_size
        
        LEARNING: Testing permissions and role-based restrictions
        """
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'farm_size': '5.5'
        }
        
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        # Should return 400 with error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('farm_size', response.data['error'])
    
    def test_coop_can_update_business_name(self):
        """
        TEST 5: Co-ops can update business_name
        """
        self.client.force_authenticate(user=self.coop)
        
        data = {
            'business_name': 'Farmers United Co-op'
        }
        
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coop.refresh_from_db()
        self.assertEqual(self.coop.business_name, 'Farmers United Co-op')
    
    def test_farmer_cannot_update_business_name(self):
        """
        TEST 6: Farmers should NOT be able to set business_name
        """
        self.client.force_authenticate(user=self.farmer)
        
        data = {
            'business_name': 'My Farm Business'
        }
        
        response = self.client.patch('/api/users/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_name', response.data['error'])


class ProfileCompletionTests(TestCase):
    """
    Test Profile Completion Calculation
    
    LEARNING: Testing computed properties (@property methods)
    """
    
    def setUp(self):
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='',  # Empty initially
            last_name='',
            role='farmer'
        )
    
    def test_base_profile_completion(self):
        """
        TEST 7: New user should have 10% completion (email + phone)
        
        LEARNING: Testing @property methods
        """
        # New user with only email and phone
        completion = self.farmer.profile_completion
        self.assertEqual(completion, 10)
    
    def test_profile_completion_with_names(self):
        """
        TEST 8: Adding names increases completion
        """
        self.farmer.first_name = 'John'
        self.farmer.last_name = 'Doe'
        self.farmer.save()
        
        # 10 (base) + 10 (first_name) + 10 (last_name) = 30
        self.assertEqual(self.farmer.profile_completion, 30)
    
    def test_profile_completion_with_location(self):
        """
        TEST 9: Adding location increases completion significantly
        """
        self.farmer.first_name = 'John'
        self.farmer.last_name = 'Doe'
        self.farmer.location = Point(3.3792, 6.5244)
        self.farmer.location_text = 'Lagos'
        self.farmer.save()
        
        # 10 + 10 + 10 + 20 (location) + 10 (location_text) = 60
        self.assertEqual(self.farmer.profile_completion, 60)
    
    def test_farmer_profile_completion_with_farm_size(self):
        """
        TEST 10: Farmer-specific fields increase completion
        """
        self.farmer.first_name = 'John'
        self.farmer.last_name = 'Doe'
        self.farmer.location = Point(3.3792, 6.5244)
        self.farmer.location_text = 'Lagos'
        self.farmer.farm_size = Decimal('5.0')
        self.farmer.bio = 'I grow rice'
        self.farmer.save()
        
        # 60 (base) + 20 (farm_size) + 10 (bio) = 90
        self.assertEqual(self.farmer.profile_completion, 90)
    
    def test_buyer_profile_completion_with_bio(self):
        """
        TEST 11: Buyer gets 30% for bio (different from farmer)
        """
        buyer = User.objects.create_user(
            email='buyer@test.com',
            phone_number='08087654321',
            password='testpass123',
            first_name='Jane',
            last_name='Buyer',
            role='buyer'
        )
        
        buyer.bio = 'I buy agricultural products'
        buyer.save()
        
        # 10 (base) + 10 (first) + 10 (last) + 30 (bio for buyer) = 60
        self.assertEqual(buyer.profile_completion, 60)


class TrustBadgeTests(TestCase):
    """
    Test Trust Badge Creation and Level Calculation
    
    LEARNING: Testing model signals and automatic creation
    """
    
    def test_badge_created_automatically_on_user_creation(self):
        """
        TEST 12: Badge should be created automatically when user is created
        
        LEARNING: Testing Django signals
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        # Check that badge was created
        self.assertTrue(hasattr(user, 'badge'))
        self.assertEqual(user.badge.badge_level, 'new_user')
        self.assertTrue(user.badge.is_phone_verified)
    
    def test_badge_level_calculation_bronze(self):
        """
        TEST 13: Badge level should upgrade to bronze with 5+ transactions and 4.0+ rating
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 5
        badge.average_rating = Decimal('4.0')
        badge.calculate_badge_level()
        
        self.assertEqual(badge.badge_level, 'bronze')
    
    def test_badge_level_calculation_silver(self):
        """
        TEST 14: Badge level should upgrade to silver with 20+ transactions and 4.3+ rating
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 20
        badge.average_rating = Decimal('4.5')
        badge.calculate_badge_level()
        
        self.assertEqual(badge.badge_level, 'silver')
    
    def test_badge_level_calculation_gold(self):
        """
        TEST 15: Badge level should upgrade to gold with 50+ transactions and 4.7+ rating
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 50
        badge.average_rating = Decimal('4.8')
        badge.calculate_badge_level()
        
        self.assertEqual(badge.badge_level, 'gold')
    
    def test_badge_level_calculation_diamond(self):
        """
        TEST 16: Badge level should upgrade to diamond with 100+ transactions and 4.8+ rating
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 100
        badge.average_rating = Decimal('4.9')
        badge.calculate_badge_level()
        
        self.assertEqual(badge.badge_level, 'diamond')
    
    def test_badge_stays_new_user_with_low_stats(self):
        """
        TEST 17: Badge should remain new_user if requirements not met
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 3
        badge.average_rating = Decimal('3.5')
        badge.calculate_badge_level()
        
        self.assertEqual(badge.badge_level, 'new_user')


class UserSearchTests(TestCase):
    """
    Test User Search Functionality
    
    LEARNING: Testing API endpoints with query parameters
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users with different roles and locations
        self.farmer1 = User.objects.create_user(
            email='farmer1@test.com',
            phone_number='08012345671',
            password='testpass123',
            first_name='John',
            last_name='Farmer',
            role='farmer',
            location=Point(3.3792, 6.5244),  # Lagos
            location_text='Lagos'
        )
        
        self.farmer2 = User.objects.create_user(
            email='farmer2@test.com',
            phone_number='08012345672',
            password='testpass123',
            first_name='Mary',
            last_name='Grower',
            role='farmer',
            location=Point(3.9, 7.4),  # Ibadan (different location)
            location_text='Ibadan'
        )
        
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            phone_number='08012345673',
            password='testpass123',
            first_name='Jane',
            last_name='Buyer',
            role='buyer',
            location=Point(3.3792, 6.5244),  # Lagos
            location_text='Lagos'
        )
        
        # Authenticated user for searches
        self.searcher = User.objects.create_user(
            email='searcher@test.com',
            phone_number='08012345674',
            password='testpass123',
            first_name='Search',
            last_name='User',
            role='buyer'
        )
    
    def test_search_users_by_role(self):
        """
        TEST 18: Search users by role
        
        LEARNING: Testing query parameters
        """
        self.client.force_authenticate(user=self.searcher)
        
        response = self.client.get('/api/users/search/', {'role': 'farmer'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 2 farmers (excluding the searcher)
        self.assertEqual(response.data['count'], 2)
    
    def test_search_users_by_name(self):
        """
        TEST 19: Search users by name
        """
        self.client.force_authenticate(user=self.searcher)
        
        response = self.client.get('/api/users/search/', {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'John Farmer')
    
    def test_search_users_by_location(self):
        """
        TEST 20: Search users by location (within radius)
        
        LEARNING: Testing GeoDjango queries
        """
        self.client.force_authenticate(user=self.searcher)
        
        # Search near Lagos coordinates
        response = self.client.get('/api/users/search/', {
            'location_lat': 6.5244,
            'location_lng': 3.3792,
            'radius': 10  # 10km radius
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find farmer1 and buyer (both in Lagos), not farmer2 (Ibadan)
        self.assertEqual(response.data['count'], 2)
    
    def test_search_excludes_current_user(self):
        """
        TEST 21: Search should not return the current user
        """
        self.client.force_authenticate(user=self.searcher)
        
        response = self.client.get('/api/users/search/', {'search': 'Search'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not find the searcher themselves
        self.assertEqual(response.data['count'], 0)
    
    def test_search_requires_authentication(self):
        """
        TEST 22: Unauthenticated users cannot search
        
        LEARNING: Testing permission requirements
        """
        # Don't authenticate
        response = self.client.get('/api/users/search/')
        
        # Should return 401 Unauthorized or 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class UserActivityTests(TestCase):
    """
    Test Activity Logging and Retrieval
    
    LEARNING: Testing activity tracking
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
    
    def test_activity_logging(self):
        """
        TEST 23: Activity should be logged correctly
        
        LEARNING: Testing the log_activity classmethod
        """
        activity = UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description='User logged in',
            metadata={'ip': '127.0.0.1'}
        )
        
        self.assertIsNotNone(activity)
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.action_type, UserActivity.ActionTypes.LOGIN)
        self.assertEqual(activity.description, 'User logged in')
    
    def test_activity_retrieval(self):
        """
        TEST 24: User can retrieve their own activities
        """
        # Create some activities
        UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description='Login 1'
        )
        UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.PROFILE_UPDATE,
            description='Profile updated'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/activity/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_activity_filtering_by_type(self):
        """
        TEST 25: Activities can be filtered by action type
        """
        # Create different types of activities
        UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description='Login 1'
        )
        UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description='Login 2'
        )
        UserActivity.log_activity(
            user=self.user,
            action_type=UserActivity.ActionTypes.PROFILE_UPDATE,
            description='Profile updated'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/activity/', {'action_type': 'login'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_user_cannot_see_other_users_activities(self):
        """
        TEST 26: Users should only see their own activities
        
        LEARNING: Testing data isolation
        """
        other_user = User.objects.create_user(
            email='other@test.com',
            phone_number='08087654321',
            password='testpass123',
            first_name='Other',
            last_name='User',
            role='buyer'
        )
        
        # Create activity for other user
        UserActivity.log_activity(
            user=other_user,
            action_type=UserActivity.ActionTypes.LOGIN,
            description='Other user login'
        )
        
        # Authenticate as self.user
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/activity/')
        
        # Should not see other user's activities
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class EdgeCaseTests(TestCase):
    """
    Test Edge Cases and Error Handling
    
    LEARNING: Always test edge cases!
    """
    
    def test_user_with_no_location(self):
        """
        TEST 27: User without location should handle gracefully
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
            # No location set
        )
        
        # Should not crash
        self.assertIsNone(user.location)
        # Profile completion should still work
        self.assertGreaterEqual(user.profile_completion, 0)
    
    def test_profile_completion_never_exceeds_100(self):
        """
        TEST 28: Profile completion should never exceed 100%
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        # Fill all fields
        user.location = Point(3.3792, 6.5244)
        user.location_text = 'Lagos'
        user.farm_size = Decimal('10.0')
        user.bio = 'Test bio'
        user.profile_photo = 'http://example.com/photo.jpg'
        user.save()
        
        completion = user.profile_completion
        self.assertLessEqual(completion, 100)
    
    def test_search_with_invalid_coordinates(self):
        """
        TEST 29: Invalid coordinates in search should return error
        """
        client = APIClient()
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        client.force_authenticate(user=user)
        response = client.get('/api/users/search/', {
            'location_lat': 'invalid',
            'location_lng': 'invalid'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_badge_with_null_rating(self):
        """
        TEST 30: Badge calculation should handle null ratings
        """
        user = User.objects.create_user(
            email='test@test.com',
            phone_number='08012345678',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='farmer'
        )
        
        badge = user.badge
        badge.transaction_count = 10
        badge.average_rating = None  # No rating yet
        badge.calculate_badge_level()
        
        # Should stay new_user with null rating
        self.assertEqual(badge.badge_level, 'new_user')


"""
HOW TO RUN THESE TESTS:
======================

1. Run all tests:
   /home/d3mxn/Documents/notebooks/.venv312/bin/python manage.py test apps.user

2. Run specific test class:
   /home/d3mxn/Documents/notebooks/.venv312/bin/python manage.py test apps.user.tests.ProfileCompletionTests

3. Run specific test method:
   /home/d3mxn/Documents/notebooks/.venv312/bin/python manage.py test apps.user.tests.ProfileCompletionTests.test_base_profile_completion

4. Run with verbose output:
   /home/d3mxn/Documents/notebooks/.venv312/bin/python manage.py test apps.user --verbosity=2

5. Run with coverage (install coverage first: pip install coverage):
   /home/d3mxn/Documents/notebooks/.venv312/bin/coverage run --source='apps.user' manage.py test apps.user
   /home/d3mxn/Documents/notebooks/.venv312/bin/coverage report
   /home/d3mxn/Documents/notebooks/.venv312/bin/coverage html  # Creates htmlcov/index.html

TESTING BEST PRACTICES:
======================
1. Test one thing per test method
2. Use descriptive test names (test_what_should_happen_when)
3. Follow AAA pattern: Arrange, Act, Assert
4. Test both success and failure cases
5. Test edge cases and boundary conditions
6. Keep tests independent (don't rely on test order)
7. Use setUp() for common test data
8. Clean up after tests (Django does this automatically with transactions)

COMMON ASSERTIONS:
=================
self.assertEqual(a, b)           # a == b
self.assertNotEqual(a, b)        # a != b
self.assertTrue(x)               # bool(x) is True
self.assertFalse(x)              # bool(x) is False
self.assertIsNone(x)             # x is None
self.assertIsNotNone(x)          # x is not None
self.assertIn(a, b)              # a in b
self.assertNotIn(a, b)           # a not in b
self.assertGreater(a, b)         # a > b
self.assertLess(a, b)            # a < b
self.assertAlmostEqual(a, b)     # round(a-b, 7) == 0
"""
