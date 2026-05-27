import base64

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Pereval, User
from services.pereval_services import PerevalService

TEST_IMAGE_BASE64 = base64.b64encode(
    b'test image content'
).decode('utf-8')

def get_test_data():
    return {
        "beauty_title": "пер. ",
        "title": "Пхия",
        "other_titles": "Триев",
        "connect": "",
        "add_time": "2021-09-22 13:18:13",
        "user": {
            "email": "qwerty@mail.ru",
            "fam": "Пупкин",
            "name": "Василий",
            "otc": "Иванович",
            "phone": "+7 555 55 55"
        },
        "coords": {
            "latitude": "45.3842",
            "longitude": "7.1525",
            "height": "1200"
        },
        "level": {
            "winter": "",
            "summer": "1А",
            "autumn": "1А",
            "spring": ""
        },
        "images": [
            {
                "data": TEST_IMAGE_BASE64,
                "title": "Седловина"
            }
        ]
    }


class SubmitDataApiTestCase(APITestCase):

    def test_post_submit_data_and_get_by_id(self):
        data = get_test_data()

        response = self.client.post(
            "/submitData/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], 200)
        self.assertIsNone(response.data["message"])
        self.assertIsNotNone(response.data["id"])

        pereval_id = response.data["id"]

        get_response = self.client.get(f"/submitData/{pereval_id}/")

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["id"], pereval_id)
        self.assertEqual(get_response.data["title"], "Пхия")
        self.assertEqual(get_response.data["status"], "new")
        self.assertEqual(
            get_response.data["user"]["email"],
            "qwerty@mail.ru"
        )
        self.assertEqual(
            get_response.data["coords"]["height"],
            1200
        )

    def test_get_submit_data_by_user_email(self):
        data = get_test_data()

        post_response = self.client.post(
            "/submitData/",
            data,
            format="json"
        )

        self.assertEqual(post_response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            "/submitData/?user__email=qwerty@mail.ru"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Пхия")
        self.assertEqual(
            response.data[0]["user"]["email"],
            "qwerty@mail.ru"
        )

    def test_patch_submit_data_success(self):
        data = get_test_data()

        post_response = self.client.post(
            "/submitData/",
            data,
            format="json"
        )

        pereval_id = post_response.data["id"]

        update_data = get_test_data()
        update_data["title"] = "Пхия обновлённый"

        patch_response = self.client.patch(
            f"/submitData/{pereval_id}/",
            update_data,
            format="json"
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["state"], 1)
        self.assertIsNone(patch_response.data["message"])

        get_response = self.client.get(f"/submitData/{pereval_id}/")

        self.assertEqual(
            get_response.data["title"],
            "Пхия обновлённый"
        )

    def test_patch_submit_data_forbidden_if_status_not_new(self):
        data = get_test_data()

        post_response = self.client.post(
            "/submitData/",
            data,
            format="json"
        )

        pereval_id = post_response.data["id"]

        pereval = Pereval.objects.get(id=pereval_id)
        pereval.status = "accepted"
        pereval.save()

        update_data = get_test_data()
        update_data["title"] = "Нельзя обновить"

        patch_response = self.client.patch(
            f"/submitData/{pereval_id}/",
            update_data,
            format="json"
        )

        self.assertEqual(
            patch_response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(patch_response.data["state"], 0)
        self.assertEqual(
            patch_response.data["message"],
            "Редактировать можно только записи со статусом new"
        )

    def test_post_submit_data_bad_request(self):
        data = get_test_data()
        del data["title"]

        response = self.client.post(
            "/submitData/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], 400)
        self.assertIsNone(response.data["id"])
