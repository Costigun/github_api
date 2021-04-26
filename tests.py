class AccountsTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(email='foo@mail.ru')
        self.profile = UserProfileFactory(phone='0777320747', user=self.user)
        self.create_url = reverse('user_profile:create')

    def test_create_user(self):
        data = {

        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_short_password(self):
        data = {

        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_no_password(self):
        data = {

        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_too_long_username(self):
        data = {

        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_no_username(self):
        data = {

        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_created_phone(self):
        data = {

        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthorizationTest(APITestCase):

    def setUp(self):
        self.user = UserFactory(email='foo@mail.ru')
        self.test_data = ({
            "username": "test@mail.ru",
            "password": "root1admin2"
        })
        self.create_url = reverse('user_profile:login')

    def test_login_with_bad_user(self):
        data = {
            "email": "ch@mail.com",
            "password": "wowfewfow33"
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_with_bad_password(self):
        data = {
            "email": "maximneveraa@gmail.com",
            "password": "111"
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserProfileListTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(email='fofofofolo@gmail.com', username='Lala', is_staff=True)
        self.profile = UserProfileFactory(user=self.user, name='Jimmy', last_name='Jimmy',
                                          phone='0709022253', organization_info='Men', address='blabla')
        self.token = TokenFactory(user=self.user)

        self.user1 = UserFactory(email='1fofofofolo@gmail.com', is_staff=True)
        self.profile1 = UserProfileFactory(user=self.user1, name='Hochu', last_name='Igrat',
                                           phone='0709022256', organization_info='3a', address='pudga')
        self.token1 = TokenFactory(user=self.user1)
        self.client = APIClient()

        self.user_profile_url = reverse('user_profile:profile-list')

    def test_get_profile_info_successfully(self):
        profile_expected_data = [
            {'id': self.user.user_profile.id, 'name': 'Jimmy', 'last_name': 'Jimmy', 'phone': '0709022253',
             'organization_info': 'Men', 'address': 'blabla', 'photo': None, 'about_us': None}]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.user_profile_url)
        self.assertEqual(json.loads(response.content), profile_expected_data)

        # For second user it would change

        profile_expected_data = [
            {'id': self.user1.user_profile.id, 'name': 'Hochu', 'last_name': 'Igrat', 'phone': '0709022256',
             'organization_info': '3a',
             'address': 'pudga', 'photo': None, 'about_us': None}]

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(self.user_profile_url)
        self.assertEqual(json.loads(response.content), profile_expected_data)

    def test_get_profile_without_authorization(self):
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileDetailsTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(email='fofofofolo@gmail.com', username='Lala', is_staff=True)
        self.profile = UserProfileFactory(user=self.user, name='Jimmy', last_name='Jimmy',
                                          phone='0709022253', organization_info='Men', address='blabla')
        self.token = TokenFactory(user=self.user)
        self.client = APIClient()

        self.user1 = UserFactory(email='1fofofofolo@gmail.com', is_staff=True)
        self.profile1 = UserProfileFactory(user=self.user1, name='Hochu', last_name='Igrat',
                                           phone='0709022256', organization_info='3a', address='pudga')
        self.token1 = TokenFactory(user=self.user1)
        self.client = APIClient()

    def test_get_firsts_user_profile_detail_successfully(self):
        expected_data = {'id': self.user.user_profile.id, 'name': 'Jimmy', 'last_name': 'Jimmy',
                         'phone': '0709022253',
                         'organization_info': 'Men', 'address': 'blabla', 'photo': None, 'about_us': None}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user_profile_detail_url = reverse('user_profile:profile-detail',
                                               kwargs={'pk': self.user.user_profile.id})
        response = self.client.get(self.user_profile_detail_url)
        self.assertEqual(json.loads(response.content), expected_data)

    def test_get_second_user_profile_with_first_user_error(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user_profile_detail_url = reverse('user_profile:profile-detail',
                                               kwargs={'pk': self.user1.user_profile.id})
        response = self.client.get(self.user_profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserProfileUpdateTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(email='fofofofolo@gmail.com', username='Lala', is_staff=True)
        self.profile = UserProfileFactory(user=self.user, name='Jimmy', last_name='Jimmy',
                                          phone='0709022253', organization_info='Men', address='blabla')
        self.token = TokenFactory(user=self.user)

        self.user1 = UserFactory(email='1fofofofolo@gmail.com', is_staff=True)
        self.profile1 = UserProfileFactory(user=self.user1, name='Hochu', last_name='Igrat',
                                           phone='0709022256', organization_info='3a', address='pudga')
        self.token1 = TokenFactory(user=self.user1)
        self.client = APIClient()

    def test_update_firsts_user_profile_successfully(self):
        data_for_update = {'name': 'Johny', 'last_name': 'Jimmy',
                           'phone': '0709022250',
                           'organization_info': 'ss', 'address': 'ss', 'photo': None, 'about_us': 'asfasas asda sdasd '}
        expected_data = {'id': self.user.user_profile.id, 'name': 'Johny', 'last_name': 'Jimmy',
                         'phone': '0709022250',
                         'organization_info': 'ss', 'address': 'ss', 'photo': None, 'about_us': 'asfasas asda sdasd'}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user_profile_detail_url = reverse('user_profile:profile-detail',
                                               kwargs={'pk': self.user.user_profile.id})
        response = self.client.put(self.user_profile_detail_url, data_for_update, format='json')
        self.assertEqual(json.loads(response.content), expected_data)

    def test_update_user_profile_with_another_user_error(self):
        data_for_update = {'name': 'Johny', 'last_name': 'Jimmy',
                           'phone': '0709022250',
                           'organization_info': 'ss', 'address': 'ss', 'photo': None, 'about_us': 'asfasas asda sdasd '}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user_profile_detail_url = reverse('user_profile:profile-detail',
                                               kwargs={'pk': self.user1.user_profile.id})
        response = self.client.put(self.user_profile_detail_url, data_for_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_profile_without_authorization_error(self):
        data_for_update = {'name': 'Johny', 'last_name': 'Jimmy',
                           'phone': '0709022250',
                           'organization_info': 'ss', 'address': 'ss', 'photo': None, 'about_us': 'asfasas asda sdasd '}
        self.user_profile_detail_url = reverse('user_profile:profile-detail',
                                               kwargs={'pk': self.user1.user_profile.id})
        response = self.client.put(self.user_profile_detail_url, data_for_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
