from middleware.prompt_injector import inject_system_prompt as prompt_injector
from middleware.tests.consts import *
from middleware.consts import *


def test_injects_system_prompt_when_first_message_is_user():
    messages = [{MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}]
    system_prompt = TEST_SYSTEM_PROMPT

    result = prompt_injector(messages, system_prompt)

    assert result[FIRST_MESSAGE_INDEX][MESSAGE_ROLE] == SYSTEM_ROLE
    assert result[FIRST_MESSAGE_INDEX][MESSAGE_CONTENT] == system_prompt
    assert result[SECOND_MESSAGE_INDEX] == {MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}


def test_merges_when_first_message_is_already_system():
    messages = [{MESSAGE_ROLE: SYSTEM_ROLE, MESSAGE_CONTENT: SYSTEM_CONTENT}, {MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}]
    system_prompt = TEST_SYSTEM_PROMPT

    result = prompt_injector(messages, system_prompt)

    assert result[FIRST_MESSAGE_INDEX][MESSAGE_ROLE] == SYSTEM_ROLE
    assert result[FIRST_MESSAGE_INDEX][MESSAGE_CONTENT] == f"{TEST_SYSTEM_PROMPT}\n\n{SYSTEM_CONTENT}"
    assert result[SECOND_MESSAGE_INDEX] == {MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}


def test_returns_only_system_prompt_when_messages_empty():
    messages = []
    system_prompt = TEST_SYSTEM_PROMPT

    result = prompt_injector(messages, system_prompt)

    assert result == [{MESSAGE_ROLE: SYSTEM_ROLE, MESSAGE_CONTENT: system_prompt}]


def test_does_not_mutate_original_messages():
    messages = [{MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}]
    original = [{MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}]

    prompt_injector(messages, TEST_SYSTEM_PROMPT)

    assert messages == original