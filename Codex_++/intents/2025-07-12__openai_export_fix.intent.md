Added validation for _extract_messages returning None in parse_chatgpt_export.
Now raises ValueError if no messages can be parsed from a conversation.
