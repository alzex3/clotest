from time import time
import random
from httpx import Auth, Client
from environs import Env

env = Env()

CLOUDIKE_HOST_ENVS = {
    "frontend-dev": {
        "api_url": env("CLOUDIKE_FRONTEND_DEV_API_URL"),
        "admin_login": env("CLOUDIKE_FRONTEND_DEV_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_FRONTEND_DEV_ADMIN_PASSWORD")
    },
    "stage": {
        "api_url": env("CLOUDIKE_STAGE_API_URL"),
        "admin_login": env("CLOUDIKE_STAGE_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_STAGE_ADMIN_PASSWORD")
    },
    "prod-kr": {
        "api_url": env("CLOUDIKE_PROD_KR_API_URL"),
        "admin_login": env("CLOUDIKE_PROD_KR_ADMIN_LOGIN"),
        "admin_password": env("CLOUDIKE_PROD_KR_ADMIN_PASSWORD")
    }
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
        self.admin_token: str = self.get_user_token(self.admin_login, self.admin_password)
    
    def get_user_token(self, login: str, password: str) -> str:
        url = f"{self.api_url}/accounts/login/"
        data = {"login": login, "password": password}

        resp = self.client.post(url, data=data)
        return resp.json()["token"]
    
    def get_random_name(self) -> str:
        return random.choice(self.user_names)
    
    def get_random_email(self) -> str:
        return f"{self.get_random_company_name}@test.com",
    
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
            "name": name or self.get_random_company_name(),
            "email": email or self.get_random_email(),
            "password": password or self.user_password,
            "company_name": company_name or self.get_random_company_name(),
            "company_plan": company_plan or self.get_random_company_plan(),
        }
        
        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()

        data.update(company_id=resp_data["company_id"])
        return data
