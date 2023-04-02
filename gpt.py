import openai
from dotenv import dotenv_values

from utils import write_json_to_file

CONFIG = dotenv_values('.env')
OPENAI_API_KEY = CONFIG['OPENAI_API_KEY']

SESSION_FILE = 'current_session.json'

openai.api_key = OPENAI_API_KEY


class TokensLimitExceeded(Exception):

    def __init__(self, incomplete_response: str):
        self.incomplete_response = incomplete_response


class ChatSession:

    def __init__(self, messages=None):
        if messages is None:
            self.__messages = []
        else:
            self.__messages = messages

        write_json_to_file(self.__messages, SESSION_FILE)

    def _add_message(self, role: str, message: str) -> None:
        api_message = {
            "role": role,
            "content": message
        }
        self.__messages.append(api_message)
        write_json_to_file(self.__messages, SESSION_FILE)

    def send_message(self, message: str) -> str:
        self._add_message(role="user", message=message)

        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.__messages
        )

        res_first_choice = res['choices'][0]
        finish_reason = res_first_choice['finish_reason']
        response_message = res_first_choice['message']

        self._add_message(
            role=response_message['role'],
            message=response_message['content']
        )

        message_content = response_message['content']

        if finish_reason == 'length':
            raise TokensLimitExceeded(
                incomplete_response=message_content
            )
        return message_content
