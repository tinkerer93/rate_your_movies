from copy import deepcopy
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from rest_framework.test import APIClient
from .models import User


class BaseUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = {
            "first_name": "Jonh",
            "last_name": "Doe",
            "email": "mock@gmail.com",
            "password": "12345"
        }
        self.invalid_user = {
            "first_name": "Andrew",
            "last_name": "42"
        }
        self.user_data = self.client.post('/user/create',
                                          data=json.dumps(self.user, cls=DjangoJSONEncoder),
                                          content_type='application/json')
        self.auth_token = self.client.post('/user/auth',
                                           data=json.dumps({"email": self.user["email"],
                                                            "password": self.user["password"]},
                                                            cls=DjangoJSONEncoder),
                                           content_type='application/json',
                                           ).data['token']

    def tearDown(self):
        try:
            user = User.objects.get(email=self.user["email"])
            user.delete()
        except ObjectDoesNotExist:
            pass


class CreateUserViewTest(BaseUserViewTest):
    def test_create_new_user_success(self):
        user = deepcopy(self.user)
        user["email"] = "gibberish@gmail.com"
        resp = self.client.post('/user/create',
                                data=json.dumps(user, cls=DjangoJSONEncoder),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["email"], user["email"])

    def test_create_new_user_fail(self):
        resp = self.client.post('/user/create',
                                data=json.dumps(self.invalid_user, cls=DjangoJSONEncoder),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 400)


class UsersViewTest(BaseUserViewTest):

    def test_get_all_users(self):
        resp = self.client.get('/user/', content_type="application/json")
        self.assertEqual(resp.data, [self.user_data.data])
        self.assertEqual(resp.status_code, 200)


class UserDetailViewTest(BaseUserViewTest):
    def test_get_user_details(self):
        resp = self.client.get(f'/user/{self.user_data.data["id"]}',
                               content_type="application/json",
                               HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, self.user_data.data)
        resp = self.client.get(f'/user/{self.user_data.data["id"]}',
                               content_type="application/json")
        self.assertEqual(resp.status_code, 401)

    def test_put_user_details(self):
        input_params = {"id": self.user_data.data["id"], "first_name": "Jane", "last_name": "Doe",
                        "password": self.user["password"],
                        "email": "mock@gmail.com",
                        "registration_date": self.user_data.data["registration_date"],
                        "posts": []}
        resp = self.client.put(f'/user/{self.user_data.data["id"]}',
                               data=json.dumps(input_params, cls=DjangoJSONEncoder),
                               content_type="application/json",
                               HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        changed_data = deepcopy(self.user_data.data)
        changed_data.update(input_params)
        del changed_data["password"]
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, changed_data)
        resp = self.client.put(f'/user/{self.user_data.data["id"]}',
                               data=json.dumps(input_params, cls=DjangoJSONEncoder),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="Bearer abc")
        self.assertEqual(resp.status_code, 401)

    def test_delete_user(self):
        resp = self.client.delete(f'/user/{self.user_data.data["id"]}',
                                  content_type="application/json",
                                  HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 204)
        with self.assertRaises(ObjectDoesNotExist) as exc:
            user = User().get_user_by_params(email=self.user["email"])
        self.assertEqual("User matching query does not exist.", str(exc.exception))
        invalid_resp = self.client.delete(f'/user/{self.user_data.data["id"]}',
                                            content_type="application/json")
        self.assertEqual(invalid_resp.status_code, 401)


class UserAuthenticationViewTest(BaseUserViewTest):
    def test_authentication_success(self):
        resp = self.client.post(f'/user/auth',
                               data=json.dumps({"email": self.user["email"], "password": self.user["password"]},
                                                cls=DjangoJSONEncoder),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["name"], f"{self.user['first_name']} {self.user['last_name']}")

    def test_authentication_fail(self):
        resp = self.client.post(f'/user/auth',
                               data=json.dumps({"email": "invalid@mail.com", "password": "password"},
                                                cls=DjangoJSONEncoder),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data, {"error": "Cannot authenticate user with the credentials given."})
