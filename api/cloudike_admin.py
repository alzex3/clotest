def get_company_admin(
        self,
        company_id: int,
    ) -> dict:
        url = f"{self.api_url}/admin/find_companies/"
        auth = CloudikeAuth(self.admin_token)

        params = {"company_id_in": {company_id}, "limit": 1}

        resp = self.client.post(url, params=params, auth=auth)
        resp_data = resp.json()

        return resp_data

def create_user(
        self,
        company_id: int,
        name: str = None,
        email: str = None,
        password: str = None,
    ) -> dict:
        url = f"{self.api_url}/admin/create_user/"
        auth = CloudikeAuth(self.admin_token)

        data = {
            "name": name or self.get_random_name(),
            "login": f"email:{email or self.get_random_email()}",
            "password": password or self.user_password,
        }

        resp = self.client.post(url, data=data, auth=auth)
        resp_data = resp.json()

        data.update(user_id=resp_data["userid"], company_id=resp_data["company_id"])
        return data
