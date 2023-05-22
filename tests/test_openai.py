import pytest

from llmo.llms import OpenAI


@pytest.fixture
def openai():
    return OpenAI()


def test_add_personality(openai):
    openai.add_personality()
    assert openai.personality_prompt in openai.system_prompt


def test_remove_personality(openai):
    openai.add_personality()
    openai.remove_personality()
    assert openai.personality_prompt not in openai.system_prompt


def test_submit(openai, monkeypatch):
    def mock_completion(*args, **kwargs):
        return {"choices": [
            {"message": {"role": "assistant", "content": "Python:\n```python\nprint('Hello, World!')\n```"}}]}

    monkeypatch.setattr("llmo.llms.openai.ChatCompletion.create", mock_completion)
    response = openai.submit("How to print 'Hello, World!' in Python?")
    assert "Python:\n```python\nprint('Hello, World!')\n```" in response
