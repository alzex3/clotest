import random
from time import time

from environs import Env
from httpx import Auth, Client

env = Env()

CLOUDIKE_HOST_ENVS = {
    "frontend-dev": {
        "api_url": env("CLOUDIKE_FRONTEND_DEV_API_URL"),
        "admin_login": env("CLOUDIKE_FRONTEND_DEV_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_FRONTEND_DEV_ADMIN_PASSWORD"),
    },
    "stage": {
        "api_url": env("CLOUDIKE_STAGE_API_URL"),
        "admin_login": env("CLOUDIKE_STAGE_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_STAGE_ADMIN_PASSWORD"),
    },
    "prod-kr": {
        "api_url": env("CLOUDIKE_PROD_KR_API_URL"),
        "admin_login": env("CLOUDIKE_PROD_KR_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_PROD_KR_ADMIN_PASSWORD"),
    },
    "prod-net": {
        "api_url": env("CLOUDIKE_PROD_NET_API_URL"),
        "admin_login": env("CLOUDIKE_PROD_NET_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_PROD_NET_ADMIN_PASSWORD"),
    },
}


class CloudikeAuth(Auth):
    def __init__(self, token: str):
        self.token: str = token

    def auth_flow(self, request):
        request.headers["Authorization"] = self.token
        yield request


class CloudikeAPI:
    def __init__(self, host: str, client: Client):
        host_env = CLOUDIKE_HOST_ENVS[host]
        self.api_url: str = host_env["api_url"]
        self.admin_login: str = host_env["admin_login"]
        self.admin_password: str = host_env["admin_password"]

        self.company_prefix: str = env("CLOUDIKE_COMPANY_PREFIX")
        self.company_plans: list = env.list("CLOUDIKE_COMPANY_PLANS")
        self.user_names: list = env.list("CLOUDIKE_USER_NAMES")
        self.user_password: str = env("CLOUDIKE_USER_PASSWORD")

        self.client: Client = client
        self.admin_token: str = self.get_user_token(
            self.admin_login, self.admin_password
        )

    def get_user_token(self, login: str, password: str) -> str:
        url = f"{self.api_url}/accounts/login/"
        data = {"login": f"email:{login}", "password": password}

        resp = self.client.post(url, data=data)
        return resp.json()["token"]

    def get_random_name(self) -> str:
        return random.choice(self.user_names)

    def get_random_group_name(self) -> str:
        return f"Group{int(time())}"

    def get_random_email(self) -> str:
        return f"{self.get_random_company_name()}@test.com"

    def get_random_company_name(self) -> str:
        return f"{self.company_prefix}{int(time())}"

    def get_random_company_plan(self) -> str:
        return random.choice(self.company_plans)

    def create_company(
        self,
        name: str = None,
        email: str = None,
        password: str = None,
        company_plan: str = None,
        company_name: str = None,
    ) -> dict:
        url = f"{self.api_url}/accounts/create/"
        auth = CloudikeAuth(self.admin_token)

        data = {
            "name": name or self.get_random_name(),
            "email": email or self.get_random_email(),
            "password": password or self.user_password,
            "company_name": company_name or self.get_random_company_name(),
            "company_plan": company_plan or self.get_random_company_plan(),
        }

        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()

        data.update(user_id=resp_data["userid"], company_id=resp_data["company_id"])
        return data

    def create_user(
        self,
        company_id: int,
        company_admin_email: str,
        company_admin_password: str,
        name: str = None,
        email: str = None,
        password: str = None,
    ) -> dict:
        company_admin_token = self.get_user_token(company_admin_email, company_admin_password)
        url = f"{self.api_url}/accounts/company/{company_id}/create_user/"
        auth = CloudikeAuth(company_admin_token)

        data = {
            "name": name or self.get_random_name(),
            "login": f"email:{email or self.get_random_email()}",
            "password": password or self.user_password,
        }

        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()

        data.update(user_id=resp_data["userid"], company_id=resp_data["company_id"])
        return data

    def create_group(
        self,
        company_admin_email: str,
        company_admin_password: str,
        name: str = None,
    ) -> dict:
        company_admin_token = self.get_user_token(company_admin_email, company_admin_password)
        url = f"{self.api_url}/groups/create/"
        auth = CloudikeAuth(company_admin_token)

        data = {"name": name or self.get_random_group_name()}

        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()
        return resp_data

    def add_to_group(
        self,
        group_id: int,
        users_ids: list[int],
        company_admin_email: str,
        company_admin_password: str,
    ) -> dict:
        company_admin_token = self.get_user_token(company_admin_email, company_admin_password)
        url = f"{self.api_url}/groups/{group_id}/add_user/"
        auth = CloudikeAuth(company_admin_token)

        data = {"user_ids": users_ids}

        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()
        return resp_data

    def get_user(self, user_id: int) -> dict:
        url = f"{self.api_url}/admin/accounts_find_users/"
        auth = CloudikeAuth(self.admin_token)

        params = {"user_id": user_id, "limit": 1}

        resp = self.client.post(url, params=params, auth=auth)
        resp_data = resp.json()

        return resp_data

    def approve_user(self, approve_hash: str) -> dict:
        url = f"{self.api_url}/accounts/approve/"

        params = {"hash": approve_hash}

        resp = self.client.get(url, params=params)
        resp_data = resp.json()

        return resp_data
