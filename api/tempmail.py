import os
from httpx import Client, Auth
import random
from time import sleep, time
import webbrowser
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from environs import Env


env = Env()


class TempMailAuth(Auth):
    def __init__(self, token: str):
        self.token: str = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def open_webbrowser(link: str) -> None:
    """Open a url in the browser ignoring error messages"""
    saverr = os.dup(2)
    os.close(2)
    os.open(os.devnull, os.O_RDWR)
    try:
        webbrowser.open(link)
    finally:
        os.dup2(saverr, 2)


@dataclass
class Message:
    """Simple data class that holds a message data."""
    _id: str
    _from: dict
    to: list
    subject: str
    intro: str
    text: str
    html: str

    def open_web(self):
        """Open a temporary html file with the mail inside in the browser."""
        with NamedTemporaryFile(mode="w", delete=False, suffix=".html") as f:

            html = self.html[0].replace("\n", "<br>").replace("\r", "")
            message = f"""<html>
            <head></head>
            <body>
            <b>from:</b> {self.from_}<br>
            <b>to:</b> {self.to}<br>
            <b>subject:</b> {self.subject}<br><br>
            {html}</body>
            </html>"""

            f.write(message)
            f.flush()
            file_name = f.name

            open_webbrowser(f"file://{file_name}")

            sleep(1)
            os.remove(file_name)


class Mailbox:
    """Representing a temporary mailbox."""

    def __init__(self, _id, address, password, client):
        self.api_url: str = env("TEMPMAIL_API_URL")
        self._id = _id
        self.address = address
        self.password = password

        self.client = client
        self.auth = TempMailAuth(self.get_token())

    def get_token(self) -> str:
        url = f"{self.api_url}/token"
        data = {"address": self.address, "password": self.password}

        resp = self.client.post(url, json=data)
        return resp.json()["token"]
    
    def get_message(self, message_id: str) -> dict:
        """Retrieve a specific message with the provided id."""
        url = f"{self.api_url}/messages/{message_id}"
        resp = self.client.get(url, auth=self.auth)
        return resp.json()
  
    def get_messages(self) -> list[Message]:
        """Retrieve a list of messages currently in the mailbox."""

        url = f"{self.api_url}/messages?page=1"
        resp = self.client.get(url, auth=self.auth)
        resp_data = resp.json()

        messages = []
        for message_data in resp_data["hydra:member"]:
            sleep(1)
            full_message = self.get_message(message_data["id"])
            messages.append(
                Message(
                    message_data["id"],
                    message_data["from"],
                    message_data["to"],
                    message_data["subject"],
                    message_data["intro"],
                    full_message["text"],
                    full_message["html"]
                )
            )

        return messages

    def _get_existing_messages_ids(self) -> list[int]:
        """Return the existing messages ids list. This will keep trying, ignoring errors."""
        while True:
            try:
                old_messages = self.get_messages()
                return list(map(lambda m: m._id, old_messages))
            except Exception:
                sleep(3)

    def wait_message(self) -> Message:
        old_messages_ids = self._get_existing_messages_ids()

        while True:
            sleep(2)
            try:
                new_messages = list(filter(lambda m: m._id not in old_messages_ids, self.get_messages()))
                if new_messages:
                    return new_messages[0]
            except Exception:
                pass
    
    def monitor_mailbox(self) -> Message:
        """Keep waiting for new messages and return when receive one."""
        while True:
            print("Waiting for new messages...")
            new_msg = self.wait_message()
            print("New message arrived!")
            return new_msg

    def delete_mailbox(self) -> bool:
        url = f"{self.api_url}/accounts/{self._id}"
        resp = self.client.delete(url, auth=self.auth)
        return resp.status_code == 204
    


class TempMailAPI:
    def __init__(self, client: Client):
        self.api_url: str = env("TEMPMAIL_API_URL")
        self.mailbox_prefix: str = env("TEMPMAIL_MAILBOX_PREFIX")
        self.mailbox_password: str = env("TEMPMAIL_MAILBOX_PASSWORD")

        self.client: Client = client
        self.domain: str = self.get_domain()

    def get_domain(self) -> str:
        """Get the available mail domains and randomly pick one."""
        url = f"{self.api_url}/domains"

        resp = self.client.get(url)
        data = resp.json()
        domains = [item["domain"] for item in data["hydra:member"]]
        return random.choice(domains)
    
    def get_random_username(self) -> str:
        return f"{self.mailbox_prefix}{int(time())}"

    def create_mailbox(self) -> Mailbox:
        address = f"{self.get_random_username()}@{self.domain}"

        url = f"{self.api_url}/accounts"
        data = {"address": address, "password": self.mailbox_password}

        resp = self.client.post(url, json=data)
        resp_data = resp.json()
    
        return Mailbox(
            resp_data["id"],
            resp_data["address"],
            self.mailbox_password,
            self.client
        )
