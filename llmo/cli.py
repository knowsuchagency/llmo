import argparse
import os
from pathlib import Path

import rich.traceback

from llmo.gui import LLMO
from llmo.constants import MODELS, DEFAULT_MAX_TOKENS
from llmo.llms import OpenAI
from llmo.shell_mode import run_shell_mode

rich.traceback.install()


def main():
    parser = argparse.ArgumentParser(
        description="chat and pair-programming from the command-line"
    )

    parser.add_argument(
        "prompt",
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
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
    parser.add_argument(
        "-n",
        "--no-personality",
        dest="personality",
        action="store_false",
        help="disable personality. can also be set with LLMO_DISABLE_PERSONALITY env var",
    )
    parser.add_argument(
        "-t",
        "--max-tokens",
        default=os.getenv("LLMO_MAX_TOKENS", DEFAULT_MAX_TOKENS),
        type=int,
        help="max tokens before truncation of old messages",
    )
    parser.add_argument(
        "-r",
        "--rich-text-mode",
        action="store_true",
        help="enable rich text mode (not recommended for programming)",
    )
    parser.add_argument(
        "-s",
        "--shell-mode",
        action="store_true",
        help="pure shell mode (no GUI)",
    )

    disable_personality_env_var = os.getenv("LLMO_DISABLE_PERSONALITY", "")

    if (
        disable_personality_env_var.lower().startswith("t")
        or disable_personality_env_var == "1"
    ):
        parser.set_defaults(personality=False)

    args = parser.parse_args()

    args.prompt = " ".join(args.prompt)

    staged_files = [Path(f) for f in args.files] if args.files else []

    for f in staged_files:
        assert f.exists(), f"File {f} does not exist"

    openai_client = OpenAI(
        model=args.model,
        api_key=args.key,
        max_tokens=args.max_tokens,
    )

    if args.personality:
        openai_client.add_personality()

    if args.shell_mode:
        files = [Path(f) for f in args.files] if args.files else []
        run_shell_mode(
            openai_client,
            prompt=args.prompt,
            files=files,
            rich_text_mode=args.rich_text_mode,
        )
    else:
        app = LLMO(
            prompt=args.prompt,
            staged_files=staged_files,
            llm_client=openai_client,
            rich_text_mode=args.rich_text_mode,
        )

        app.run()


if __name__ == "__main__":
    main()
