# LLMO (Elmo)

*Meaning:*
- Protector
- Worthy to be Loved
- Helm from God
- (**Most Importantly**) A helpful AI programming CLI tool

<img src="static/mascot.png" alt="mascot" style="width: 400px; height: auto;">   

Elmo is a command-line tool that leverages OpenAI's powerful language models to create a fully interactive chat interface for pair programming right in your terminal. 

With the **"staging area"**, you can keep files in the context window without the hassle of copying and pasting every time you make changes to your code.


## Features

- Interactive Chat: Enjoy real-time, interactive programming assistance in your terminal.
- Staging Area: Easily add files to the AI's context to update it about your ongoing coding tasks. No need to copy and paste updates.
- Model Customization: Choose the OpenAI model that fits your needs.
- Personality: By default, Elmo loves to make bodybuilding references. This can be turned off through a CLI flag or environment variable.

## Installation

The recommended way to install `llmo` is through [pipx][pipx]:

```bash
pipx install llmo
```

## Usage

Here's how you can use llmo from the command line:

```bash
# Basic usage
lm "Could you show me an example of valid json?"

# Adding files to context

# main.py
# from utils import add_numbers
# result = add_numbers(5, 3)

# utils.py
# def add_numbers(a, b):
#     return a + b

lm "How can I make add_numbers return a string?" -f "main.py" -f "utils.py"
```

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Disclaimer

This tool is not officially associated with OpenAI. Always follow OpenAI's use case policy when interacting with their API.

[pipx]: https://github.com/pypa/pipx
