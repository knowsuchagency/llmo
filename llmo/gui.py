import asyncio
from pathlib import Path
from typing import Iterable, Protocol

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
    Select, Switch,
)

from llmo.constants import MODELS
from llmo.llms import OpenAI


class LLMInterface(Protocol):
    has_personality: bool

    def submit(self, prompt: str, files: Iterable[Path] = None) -> str:
        ...

    async def asubmit(self, prompt: str, files: Iterable[Path] = None):
        ...

    def add_personality(self) -> None:
        ...

    def remove_personality(self) -> None:
        ...


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
        llm_client: LLMInterface = None,
        rich_text_mode: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.staged_files = set(staged_files) if staged_files else set()
        self.prompt = prompt
        self.current_tab = current_tab
        self.llm_client = llm_client or OpenAI()
        self.selected_file = None
        self.rich_text_mode = rich_text_mode
        self.markdown = ""

    def on_mount(self):
        input_widget = self.query_one("#prompt", Input)
        input_widget.focus()
        if self.prompt:
            self.handle_initial_submission()

    def compose(self) -> ComposeResult:
        if not self.rich_text_mode:
            response_view = TextLog(
                id="response",
                wrap=True,
                markup=True,
                highlight=True,
            )
        else:
            response_view = Markdown(
                self.markdown,
                id="response",
            )

        with Container(id="app"):
            yield Header()

            with Horizontal(id="tabs", classes="container"):
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
                                value=self.llm_client.model,
                            )
                            yield Input(
                                value=self.llm_client.api_key,
                                placeholder="API Key",
                                password=True,
                                id="api-key-input",
                            )
                            yield Label("Personality: ")
                            yield Switch(value=self.llm_client.has_personality, id="personality-switch")

                with Vertical(id="chat"):
                    with VerticalScroll(id="scroll-area"):
                        yield response_view
                    yield Input(
                        placeholder="Type here",
                        id="prompt",
                    )

        yield Footer()

    @on(Switch.Changed)
    def toggle_personality(self, event: Switch.Changed) -> None:
        self.llm_client.add_personality() if event.switch.value else self.llm_client.remove_personality()

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.llm_client.model = str(event.value)

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
        response_view = self.query_one("#response")  # noqa
        if self.rich_text_mode:
            response_view: Markdown
            self.markdown = ""
            response_view.update(self.markdown)
        else:
            response_view: TextLog
            self.llm_client.reset()
            response_view.clear()
        # clear prompt
        self.query_one("#prompt", Input).value = ""

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "prompt":
            self.prompt = event.input.value
        elif event.input.id == "api-key-input":
            self.llm_client.api_key = event.input.value
            openai.api_key = self.llm_client.api_key
        else:
            raise ValueError(f"Unknown input: {event.input.id}")

    async def on_input_submitted(self, _: Input.Submitted):
        await self.handle_submission()

    async def handle_submission(self):
        prompt_area = self.query_one("#prompt")
        loading_indicator = LoadingIndicator()
        await prompt_area.mount(loading_indicator)

        if not self.rich_text_mode:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.llm_client.submit,
                self.prompt,
                self.staged_files,
            )
            log = self.query_one("#response", TextLog)
            log.write(f">> {self.prompt}\n")
            log.write(response)
            log.write("\n\n")
        else:
            scroll_area = self.query_one("#scroll-area")
            output = self.query_one("#response", Markdown)
            self.markdown += f"{self.prompt}"
            output.update(self.markdown)
            self.markdown += "\n---\n"
            async for content in self.llm_client.asubmit(
                prompt=self.prompt,
                files=self.staged_files,
            ):
                self.markdown += content
                output.update(self.markdown)
                output.scroll_page_down()
                scroll_area.scroll_page_down()
            self.markdown += "\n---\n"
            output.update(self.markdown)
            output.scroll_page_down()
            scroll_area.scroll_page_down()

        self.query_one("#prompt", Input).value = ""
        await loading_indicator.remove()

    @work
    async def handle_initial_submission(self):
        """This runs after the app is mounted, if a prompt was passed from the CLI."""
        await self.handle_submission()
