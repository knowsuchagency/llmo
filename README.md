# LLMO (Elmo)

*Meaning:*
- Protector
- Worthy to be Loved
- Helm from God
- (**Most Importantly**) A helpful AI programming CLI tool

<img src="static/mascot.png" alt="elmo" style="width: 400px; height: auto;">   

Elmo is a command-line tool that leverages OpenAI's powerful language models to create a fully interactive chat interface for pair programming right in your terminal. 

With the **"staging area"** feature, you can add files to the context window without the hassle of copying and pasting every time.

## Installation

You can install the package via pip:
```bash
pip install llmo
```

## Features

- Interactive Chat: Enjoy real-time, interactive programming assistance in your terminal.
- Staging Area: Easily add files to the AI's context to update it about your ongoing coding tasks. No need to copy and paste updates.
- Model Customization: Choose the OpenAI model that fits your needs.
- Personality: By default, Elmo loves to make bodybuilding references. This can be turned off through a CLI flag or environment variable.

## Usage

Here's how you can use llmo from the command line:

```bash
# Basic usage
llmo "your_prompt"

# Adding files to context
llmo "your_prompt" -f "your_file.py" -f "your_other_file.py"

# Selecting model
llmo "your_prompt" -m "gpt-4"

# Passing API key
llmo "your_prompt" -k "your_openai_api_key" # this is optional

# disable AI personality
llmo "your_prompt" --no-personality

# Set max tokens
llmo "your_prompt" -t 5000
```

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Disclaimer

This tool is not officially associated with OpenAI. Always follow OpenAI's use case policy when interacting with their API.
