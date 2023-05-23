import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from llmo.llms import OpenAI


def run_shell_mode(
    openai_client: OpenAI,
    prompt=None,
    files=None,
    rich_text_mode=False,
):
    console = Console()

    async def display_content():
        response = ""
        num_lines_to_clear = 0

        async for content in openai_client.asubmit(prompt=prompt, files=files):
            response += content
            console.print(content, soft_wrap=True, end="")
            num_lines_to_clear += content.count("\n")

        if rich_text_mode and num_lines_to_clear > 0:
            for _ in range(num_lines_to_clear):
                print("\033[F\033[K", end="")

            md = Markdown(response)
            console.print(md)
        else:
            console.print()

    initial_prompt = True if prompt else False

    while True:
        if not initial_prompt:
            prompt = Prompt.ask(">> ")

            if prompt in ["exit", "clear"]:
                if prompt == "exit":
                    return
                console.clear()
                continue

        asyncio.run(display_content())
        initial_prompt = False
