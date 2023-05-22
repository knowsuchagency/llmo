# LLMO (Elmo)

*Meaning:*
- Protector
- Worthy to be Loved
- Helm from God
- (**Most Importantly**) A helpful AI programming CLI tool

<img src="https://github.com/knowsuchagency/llmo/blob/main/static/mascot.png?raw=true" alt="mascot" style="width: 400px; height: auto;">   

The full power of GPT straight from your terminal!

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
llmo --help
# you can also use the shorthand
lm

# You can pass the -s flag if you don't need the full GUI mode
lm -s "Could you show me an example of valid json?"

# Adding files to context

# main.py
# from utils import add_numbers
# result = add_numbers(5, 3)

# utils.py
# def add_numbers(a, b):
#     return a + b

lm "How can I make add_numbers return a string?" -f "main.py" -f "utils.py"
```

## Notes

[Textual][textual] runs the terminal in application mode. The means that you can't simply copy content as you normally would.
In [iterm2][iterm2], you can hold down the `option` key to select text. See the documentation for your terminal emulator for more information.

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Disclaimer

This tool is not officially associated with OpenAI. Always follow OpenAI's use case policy when interacting with their API.

[pipx]: https://github.com/pypa/pipx
[textual]: https://textual.textualize.io/
[iterm2]: https://iterm2.com/
