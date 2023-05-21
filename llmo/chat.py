import argparse
import asyncio
import os
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict, Literal, Iterable

import openai
from textual import work, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual.widgets import (
    Input,
    DirectoryTree,
    ListView,
    ListItem,
    Label,
    Button,
    Header,
    TextLog,
    ContentSwitcher,
    Footer,
    LoadingIndicator,
    Markdown,
    Select,
)

MAX_TOKENS = 4096 - 800  # gpt-3.5-turbo's max tokens minus some buffer
ESTIMATED_CHAR_PER_TOKEN = 4
MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
]


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

    def __post_init__(self):
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
            for msg in self.messages:
                if msg["role"] == "user" and msg["content"].startswith(f"`{file}`"):
                    self.messages.remove(msg)
            # add file content to messages
            self.messages.append(
                {"role": "user", "content": f"`{file}`\n```{file.read_text()}```"}
            )
        self.messages.append({"role": "user", "content": prompt})

        # truncate old messages to stay under the character limit
        estimated_tokens = sum(
            len(m["content"]) // ESTIMATED_CHAR_PER_TOKEN for m in self.messages
        )
        while estimated_tokens > MAX_TOKENS:
            removed_message = self.messages.popleft()
            estimated_tokens -= (
                len(removed_message["content"]) // ESTIMATED_CHAR_PER_TOKEN
            )

        assistant_message = openai.ChatCompletion.create(
            messages=list(self.messages),
            model=self.model,
            temperature=self.temperature,
        )["choices"][0]["message"]

        self.messages.append(assistant_message)

        return assistant_message["content"]


class LLMO(App):
    CSS_PATH = "layout.css"
    BINDINGS = [
        ("ctrl+z", "switch_tab", "Switch Tab"),
        ("ctrl+x", "reset_chat", "Reset Chat"),
        ("s", "stage_file", "Stage File"),
        ("r", "reset_stage", "Reset Staged Files"),
        ("ctrl+shift+a", "reset_all", "Reset All"),
    ]

    def __init__(
        self,
        staged_files: Iterable[Path] = None,
        prompt: str = "",
        current_tab: str = "chat",
        openai_client: OpenAI = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.staged_files = set(staged_files) if staged_files else set()
        self.prompt = prompt
        self.current_tab = current_tab
        self.openai_client = openai_client or OpenAI()
        self.response = ""
        self.selected_file = None

    def on_mount(self):
        input_widget = self.query_one("#prompt", Input)
        input_widget.focus()
        if self.prompt:
            self.handle_initial_submission()

    def compose(self) -> ComposeResult:
        with Container(id="app"):
            yield Header()

            with Horizontal(id="tabs"):
                yield Button(
                    "Context",
                    id="context-choice-button",
                    variant="warning",
                )
                yield Button(
                    "Chat",
                    id="chat-choice-button",
                    variant="primary",
                )

            with ContentSwitcher(initial=self.current_tab):
                with Container(id="context"):
                    with Horizontal():
                        with Vertical():
                            yield DirectoryTree(
                                "./",
                                id="directory-tree",
                            )
                            with Horizontal(id="button-group"):
                                yield Button(
                                    "stage file",
                                    id="stage-file-button",
                                )
                                yield Button(
                                    "reset staging area",
                                    id="reset-stage-button",
                                    variant="error",
                                )
                        with Vertical():
                            yield Markdown("## Staged Files")
                            yield ListView(
                                *(ListItem(Label(str(k))) for k in self.staged_files),
                                id="staged-files",
                            )
                            yield Markdown("## Model Settings")
                            yield Select(
                                ((m, m) for m in MODELS),
                                id="model-select",
                                value=self.openai_client.model,
                            )
                            yield Input(
                                value=self.openai_client.api_key,
                                placeholder="API Key",
                                password=True,
                                id="api-key-input",
                            )

                with Vertical(id="chat"):
                    with VerticalScroll(id="scroll-area"):
                        yield TextLog(
                            id="response",
                            wrap=True,
                            markup=True,
                            highlight=True,
                        )
                    yield Input(
                        placeholder="Type here",
                        id="prompt",
                    )

        yield Footer()

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.openai_client.model = str(event.value)

    def update_stage_file_button_variant(self):
        selected_file = self.selected_file
        stage_file_button = self.query_one("#stage-file-button", Button)
        if selected_file and selected_file not in self.staged_files:
            stage_file_button.variant = "success"
        else:
            stage_file_button.variant = "default"

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.selected_file = Path(event.path)
        self.update_stage_file_button_variant()

    def action_switch_tab(self):
        self.set_tab("chat" if self.current_tab == "context" else "context")

    def action_stage_file(self):
        if self.selected_file:
            self.staged_files.add(self.selected_file)
            staged_files_view = self.query_one("#staged-files", ListView)
            staged_files_view.clear()
            for f in self.staged_files:
                staged_files_view.append(ListItem(Label(str(f))))
            self.update_stage_file_button_variant()

    def action_reset_stage(self):
        self.staged_files.clear()
        self.query_one("#staged-files", ListView).clear()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id.endswith("-choice-button"):
            id_ = event.button.id.split("-")[0]
            self.set_tab(id_)

        if event.button.id == "stage-file-button":
            self.action_stage_file()

        elif event.button.id == "reset-stage-button":
            self.action_reset_stage()

        if event.button.id == "submit-prompt-button":
            self.action_submit()

    def set_tab(self, id_):
        self.current_tab = id_
        self.query_one(ContentSwitcher).current = self.current_tab
        if self.current_tab == "chat":
            self.query_one("#prompt", Input).focus()

    def action_reset_all(self):
        self.action_reset_chat()
        self.action_reset_stage()

    def action_reset_chat(self):
        self.response = ""
        self.query_one("#response", TextLog).clear()
        self.openai_client.reset()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "prompt":
            self.prompt = event.input.value
        elif event.input.id == "api-key-input":
            self.openai_client.api_key = event.input.value
            openai.api_key = self.openai_client.api_key
        else:
            raise ValueError(f"Unknown input: {event.input.id}")

    async def on_input_submitted(self, _: Input.Submitted):
        await self.handle_submission()

    async def handle_submission(self):
        prompt_area = self.query_one("#prompt")
        loading_indicator = LoadingIndicator()
        await prompt_area.mount(loading_indicator)
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            self.openai_client.submit,
            self.prompt,
            self.staged_files,
        )
        log = self.query_one("#response", TextLog)
        log.write(f">> {self.prompt}\n")
        log.write(response)
        log.write("\n---\n")
        self.query_one("#prompt", Input).value = ""
        await loading_indicator.remove()

    @work
    async def handle_initial_submission(self):
        """This runs after the app is mounted, if a prompt was passed from the CLI."""
        await self.handle_submission()


def main():
    parser = argparse.ArgumentParser(
        description="chat and pair-programming from the command-line"
    )

    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",
        default="",
        help="initial LLM prompt (optional)",
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        action="append",
        help="files to add to context window",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        choices=MODELS,
        default="gpt-3.5-turbo",
        help="OpenAI model to use",
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API Key",
    )

    args = parser.parse_args()

    staged_files = [Path(f) for f in args.files] if args.files else []

    for f in staged_files:
        assert f.exists(), f"File {f} does not exist"

    openai_client = OpenAI(model=args.model, api_key=args.key)

    app = LLMO(
        prompt=args.prompt,
        staged_files=staged_files,
        openai_client=openai_client,
    )

    app.run()


if __name__ == "__main__":
    main()
