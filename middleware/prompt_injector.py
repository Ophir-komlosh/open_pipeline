from copy import deepcopy
from consts import *

def inject_system_prompt(messages, system_prompt):

    messages = deepcopy(messages)

    if not messages:
        return [{MESSAGE_ROLE: SYSTEM_ROLE, MESSAGE_CONTENT: system_prompt}]

    if messages[FIRST_MESSAGE_INDEX].get(MESSAGE_ROLE) == MESSAGE_ROLE:
        messages[FIRST_MESSAGE_INDEX][MESSAGE_CONTENT] = system_prompt + "\n\n" + messages[FIRST_MESSAGE_INDEX][MESSAGE_CONTENT]
        return messages

    return [{MESSAGE_ROLE: SYSTEM_ROLE, MESSAGE_CONTENT: system_prompt}] + messages