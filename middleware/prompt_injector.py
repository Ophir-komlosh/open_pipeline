from copy import deepcopy

def inject_system_prompt(messages, system_prompt):

    messages = deepcopy(messages)

    if not messages:
        return [{"role": "system", "content": system_prompt}]

    if messages[0].get("role") == "system":
        messages[0]["content"] = system_prompt + "\n\n" + messages[0]["content"]
        return messages

    return [{"role": "system", "content": system_prompt}] + messages