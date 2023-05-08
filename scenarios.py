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

    def create_company(self, host: str) -> str:
        tempmail = TempMailAPI(self.client)
        mailbox = tempmail.create_mailbox()

        cloudike = CloudikeAPI(host, self.client)
        company = cloudike.create_company(email=mailbox.address)

        message = mailbox.monitor_mailbox()
        message_html = message.html[0]

        confirm_link = self.parse_link(message_html, "cloudike.kr")

        result = {
            "email_address": mailbox.address,
            "email_password": mailbox.password,
            "company_id": company["company_id"],
            "company_admin_email": company["email"],
            "company_admin_password": company["password"],
            "confirm_link": confirm_link,
        }

        return result
