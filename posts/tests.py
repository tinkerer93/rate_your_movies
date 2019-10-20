import json
from copy import deepcopy
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from .models import Post


class BasePostViewTest(TestCase):
    def setUp(self):
        self.user = {
            "first_name": "Jonh",
            "last_name": "Doe",
            "email": "mock@gmail.com",
            "password": "12345"
        }
        self.user_data = self.client.post('/user/create',
                                          data=json.dumps(self.user, cls=DjangoJSONEncoder),
                                          content_type='application/json')
        self.client = APIClient()

        self.test_post = {
            "title": "Joker",
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                    "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "rating": 9,
            "author": self.user_data.data["id"]
        }
        self.auth_token = self.client.post('/user/auth',
                                           data=json.dumps({"email": self.user["email"],
                                                            "password": self.user["password"]},
                                                           cls=DjangoJSONEncoder),
                                           content_type='application/json',
                                           ).data['token']
        self.post_data = self.client.post('/post/create',
                             data=json.dumps([self.test_post], cls=DjangoJSONEncoder),
                             content_type='application/json',
                             HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.post_id = self.post_data.data[0]["id"]

    def tearDown(self):
        try:
            user = User.objects.get(email=self.user["email"])
            user.delete()
        except ObjectDoesNotExist:
            pass


class CreatePostViewTest(BasePostViewTest):
    def test_post_creation_success(self):
        resp = self.client.post('/post/create',
                                data=json.dumps([self.test_post], cls=DjangoJSONEncoder),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 201)
        post = Post.objects.get(**resp.data[0])
        self.assertEqual(post.likes, 0)

    def test_post_creation_fail_no_author(self):
        invalid_post_data = deepcopy(self.test_post)
        del invalid_post_data["author"]
        resp = self.client.post('/post/create',
                                data=json.dumps(invalid_post_data, cls=DjangoJSONEncoder),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 400)

    def test_post_creation_fail_no_auth_token(self):
        resp = self.client.post('/post/create',
                                data=json.dumps(self.test_post, cls=DjangoJSONEncoder),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 401)


class PostsViewTest(BasePostViewTest):
    def test_get_all_posts(self):
        post_list = []
        for post in range(3):
            post_list.append(self.test_post)
        self.client.post('/post/create',
                         data=json.dumps(post_list, cls=DjangoJSONEncoder),
                         content_type='application/json',
                         HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        resp = self.client.get('/post/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)


class PostDetailViewTest(BasePostViewTest):
    def test_post_detail_get(self):
        resp = self.client.get(f'/post/{self.post_id}',
                         content_type='application/json',
                         HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(set(resp.data.items()) >= set(self.test_post.items()))

    def test_post_detail_put(self):
        resp = self.client.put(f'/post/{self.post_id}',
                               data=json.dumps(self.test_post, cls=DjangoJSONEncoder),
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, "Post was successfully updated.")

    def test_post_detail_delete(self):
        resp = self.client.delete(f'/post/{self.post_id}',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        self.assertEqual(resp.status_code, 204)
        with self.assertRaises(ObjectDoesNotExist) as exc:
            post = Post.objects.get(pk=self.post_id)
        self.assertEqual("Post matching query does not exist.", str(exc.exception))


class CreateLikeViewTest(BasePostViewTest):
    def test_create_like(self):
        number_of_likes = 10
        for like in range(number_of_likes):
            resp = self.client.put(f'/post/{self.post_id}/like',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f"Bearer {self.auth_token}"
                                   )
        self.assertEqual(resp.status_code, 200)
        post = Post.objects.get(pk=self.post_id)
        self.assertEqual(post.likes, number_of_likes)


class TopPostsViewTest(BasePostViewTest):
    def test_get_top_ten_posts(self):
        like_counter = 0
        post_list = []
        for post in range(11):
            post_list.append(self.test_post)
        post_data = self.client.post('/post/create',
                                data=json.dumps(post_list, cls=DjangoJSONEncoder),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        for post in post_data.data:
            for like in range(like_counter):
                Post().add_like_to_post(post["id"])
            like_counter +=1
        top_posts = self.client.get('/post/top',
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=f"Bearer {self.auth_token}")
        top_post = Post.objects.get(pk=top_posts.data[0]["id"])
        last_post = Post.objects.get(pk=top_posts.data[9]["id"])
        self.assertEqual(top_post.likes, 10)
        self.assertEqual(last_post.likes, 1)

