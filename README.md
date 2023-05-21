# LLMO (Elmo)

*Meaning:*
- Protector
- Worthy to be Loved
- Helm from God
- (**Most Importantly**) Helpful AI programming CLI tool

![elmo](static/mascot.png)

LLMO is a powerful, easy-to-use command-line chat application that leverages OpenAI's GPT-3.5-turbo to provide an interactive pair-programming experience. With LLMO, you can have a
conversation with your AI assistant, stage files for the assistant to analyze, and receive insightful responses based on the context provided.

## Features

- Interactive command-line interface
- Pair-programming with AI assistance
- Supports multiple OpenAI models
- Ability to stage files for context-aware responses
- Easy navigation between chat and context tabs
- Customizable settings

## Installation

```sh
pip install llmo
```

4. (Optional) Set up an environment variable for your OpenAI API key:

```sh
export OPENAI_API_KEY=sk-...
```

## Usage

To start the LLMO chat app, run:

```sh
lm
# or
llmo
```

Alternatively, you can provide an initial prompt and stage files for context as command-line arguments:

```sh
lm "how can I add a cli to my python script?" -f my_script.py -f utils.py
```

### Chat Tab

Type your message in the input field at the bottom of the chat tab and press `Enter` to submit. The AI assistant will analyze your prompt and provide a response based on the prompt and
staged files.

### Context Tab

Switch between the chat and context tabs by pressing `Ctrl+Z`. In the context tab, you can:

- Browse and select files from the directory tree
- Stage files for the AI assistant by pressing the "Stage File" button or pressing `S`
- Reset the staging area by pressing the "Reset Staging Area" button or pressing `R`
- Select the OpenAI model to use from the "Model Settings" dropdown
- Update the API Key from the context menu

### Additional Actions

- Reset chat by pressing `Ctrl+X`
- Reset all settings by pressing `Ctrl+Shift+A`

## License

LLMO chat app is released under the [Apache 2 License](LICENSE).
