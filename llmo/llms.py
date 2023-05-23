import asyncio
from collections import deque
from copy import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict, Literal, Iterable

import openai

from llmo.constants import ESTIMATED_CHAR_PER_TOKEN


class Message(TypedDict):
    role: Literal["user", "system", "assistant"]
    content: str


class SystemMessage(TypedDict):
    role: Literal["system"]
    content: str


@dataclass
class OpenAI:
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    messages: deque[Message] = field(default_factory=deque)
    api_key: str = None
    system_prompt: str = (
        "You are an AI programming assistant named Elmo. "
        "Think step-by-step. "
        "Make sure to include the programming language name at the start of the Markdown code blocks."
    )
    personality_prompt: str = (
        "You love creatine and bodybuilding "
        "and go out of your way to insert creative, bodybuilding, and /r/swoleacceptance references in your responses."
    )
    max_tokens: int = None

    @property
    def has_personality(self):
        return self.personality_prompt in self.system_prompt

    def add_personality(self):
        self.system_prompt = self._initial_system_prompt + " " + self.personality_prompt

    def remove_personality(self):
        self.system_prompt = self._initial_system_prompt

    def __post_init__(self):
        self._initial_system_prompt = self.system_prompt
        if self.api_key:
            openai.api_key = self.api_key

    def reset(self):
        self.messages = deque()

    def submit(self, prompt: str, files: Iterable[Path] = None):
        """
        Submit a prompt to the OpenAI API and return the response.

        If files are provided, they will be added to the prompt as part of the submission.
        """
        for file in files or []:
            # remove any existing messages with the same file content
            temp_messages = copy(self.messages)
            for msg in temp_messages:
                if msg["role"] == "user" and msg["content"].startswith(f"`{file}`"):
                    self.messages.remove(msg)
            self.messages.append(
                {"role": "user", "content": f"`{file}`\n```{file.read_text()}```"}
            )
        self.messages.append({"role": "user", "content": prompt})

        self.truncate_old_messages()

        system_message = SystemMessage(
            role="system",
            content=self.system_prompt,
        )
        messages = [system_message, *self.messages]

        assistant_message = openai.ChatCompletion.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
        )["choices"][0]["message"]

        self.messages.append(assistant_message)

        return assistant_message["content"]

    def remove_file_messages(self):
        temp_messages = copy(self.messages)
        for msg in temp_messages:
            if (
                msg["role"] == "user"
                and msg["content"].startswith("`")
                and msg["content"].endswith("```")
            ):
                self.messages.remove(msg)
                return True
        return False

    def truncate_old_messages(self):
        """Truncate old messages to stay under the character limit."""
        if self.max_tokens is not None:
            estimated_tokens = sum(
                len(m["content"]) / ESTIMATED_CHAR_PER_TOKEN for m in self.messages
            )
            while estimated_tokens > self.max_tokens:
                # Try to remove file messages first
                if not self.remove_file_messages():
                    # If no file messages to remove, remove the oldest message
                    removed_message = self.messages.popleft()
                else:
                    # If a file message was removed, continue to the next iteration
                    continue

                estimated_tokens -= (
                    len(removed_message["content"]) / ESTIMATED_CHAR_PER_TOKEN
                )

    async def asubmit(self, prompt: str, files: Iterable[Path] = None):
        """
        Submit a prompt to the OpenAI API and asynchronously yield tokens.

        If files are provided, they will be added to the prompt as part of the submission.
        """
        for file in files or []:
            # remove any existing messages with the same file content
            temp_messages = copy(self.messages)
            for msg in temp_messages:
                if msg["role"] == "user" and msg["content"].startswith(f"`{file}`"):
                    self.messages.remove(msg)
            # add file content to messages
            self.messages.append(
                {"role": "user", "content": f"`{file}`\n```{file.read_text()}```"}
            )
        self.messages.append({"role": "user", "content": prompt})

        self.truncate_old_messages()

        system_message = SystemMessage(
            role="system",
            content=self.system_prompt,
        )
        messages = [system_message, *self.messages]

        events = openai.ChatCompletion.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            stream=True,
        )

        assistant_message = {
            "role": "assistant",
            "content": "",
        }

        loop = asyncio.get_event_loop()

        while response := await loop.run_in_executor(None, next, events):
            content = response["choices"][0]["delta"].get("content")
            role = response["choices"][0]["delta"].get("role")
            finished_reason = response["choices"][0]["finish_reason"]
            if finished_reason:
                self.messages.append(assistant_message)
                return
            if role:
                continue
            elif content:
                assistant_message["content"] += content
                yield content
