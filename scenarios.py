import random

from bs4 import BeautifulSoup
from httpx import Client

from api.cloudike import CloudikeAPI
from api.tempmail import TempMailAPI


class Scenario:
    def __init__(self, client: Client):
        self.client = client

    def parse_link(self, html: str, keyword: str):
        soup = BeautifulSoup(html, "html.parser")

        a_tags = soup.find_all("a")
        for a in a_tags:
            href = a.get("href")
            if href and keyword in href:
                return href

    def create_company_fake_email(self, host: str, plan: str) -> dict:
        cloudike = CloudikeAPI(host, self.client)
        company = cloudike.create_company(company_plan=plan)

        company_admin = cloudike.get_user(user_id=company["user_id"])["users"][0]
        cloudike.approve_user(approve_hash=company_admin["approve_hash"][0])


        result = {
            "company_id": company["company_id"],
            "company_admin_email": company["email"],
            "company_admin_password": company["password"],
        }

        return result

    def create_company_real_email(self, host: str, plan: str) -> dict:
        tempmail = TempMailAPI(self.client)
        mailbox = tempmail.create_mailbox()

        cloudike = CloudikeAPI(host, self.client)
        company = cloudike.create_company(email=mailbox.address, company_plan=plan)

        message = mailbox.monitor_mailbox()
        message_html = message.html[0]

        confirm_link = self.parse_link(message_html, "cloudike.")

        result = {
            "email_address": mailbox.address,
            "email_password": mailbox.password,
            "company_id": company["company_id"],
            "company_admin_email": company["email"],
            "company_admin_password": company["password"],
            "confirm_link": confirm_link,
        }

        return result

    def create_company_users(
            self,
            host: str,
            company_id: int,
            company_admin_email: str,
            company_admin_password: str,
            count: int,
            approve: bool = False,
        ) -> dict:
        cloudike = CloudikeAPI(host, self.client)

        created_users = []
        for i in range(count):
            print(f"user_{i+1}")
            user = cloudike.create_user(company_id, company_admin_email, company_admin_password)
            if approve:
                company_admin = cloudike.get_user(user_id=user["user_id"])["users"][0]
                cloudike.approve_user(approve_hash=company_admin["approve_hash"][0])

            created_users.append(user)

        return created_users

    def create_company_group(
            self,
            host: str,
            company_admin_email: str,
            company_admin_password: str,
            count: int,
        ) -> dict:
        cloudike = CloudikeAPI(host, self.client)

        created_groups = []
        for i in range(count):
            print(f"group_{i+1}")
            user = cloudike.create_group(company_admin_email, company_admin_password)
            created_groups.append(user)

        return created_groups

    def add_to_company_group(
            self,
            host: str,
            company_admin_email: str,
            company_admin_password: str,
            group_id: int,
            users_ids: list[int],
        ) -> dict:
        cloudike = CloudikeAPI(host, self.client)
        result = cloudike.add_to_group(group_id, users_ids, company_admin_email, company_admin_password)
        return result

with Client() as client:
    scenario = Scenario(client)
    company = scenario.create_company_fake_email("frontend-dev", "professional")

    groups = scenario.create_company_group(
        "frontend-dev",
        company["company_admin_email"],
        company["company_admin_password"],
        100,
    )
    group_ids = [group["group_id"] for group in groups]

    users = scenario.create_company_users(
        "frontend-dev",
        company["company_id"],
        company["company_admin_email"],
        company["company_admin_password"],
        1000,
    )

    for i, user in enumerate(users):
        print(f"user_{i+1}_added_to_group")
        scenario.add_to_company_group(
            "frontend-dev",
            company["company_admin_email"],
            company["company_admin_password"],
            random.choice(group_ids),
            [user["user_id"]],
        )

    print(company)
