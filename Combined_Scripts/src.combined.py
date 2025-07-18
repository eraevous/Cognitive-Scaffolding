#__________________________________________________________________
# File: __init__.py
# No docstring found

#__________________________________________________________________
# File: zen_of_spite.py
# No docstring found

# zen_of_spite.py
"""
The Zen of Spite — a manifesto for the fed-up, the betrayed, and the battle-scarred.
A direct response to 'import this' and the sanctimony of 'Pythonic' dogma.
"""

spite_verses = [
    "There are fifteen inconsistent ways to do anything, and all of them are half-documented.",
    "If the method isn’t available on the object, try the module, or the class, or both.",
    "Readability counts — but only after you guess the correct paradigm.",
    "Special cases aren't special enough to break your pipeline silently.",
    "Errors should never pass silently — unless you're too lazy to raise them.",
    "In the face of ambiguity, add a decorator and pretend it’s elegant.",
    "There should be one— and preferably only one —obvious way to do it."
    " (Except for strings. And sorting. And file IO. And literally everything else.)",
    "Namespaces are one honking great idea — let’s ruin them with sys.path hacks.",
    "Simple is better than complex — but complex is what you'll get from `utils.py`.",
    "Flat is better than nested — unless you're three layers deep in a method chain.",
    "Now is better than never — especially when writing compatibility layers for Python 2.",
    "Although never is often better than *right* now — unless you're handling NoneType.",
    "If the implementation is hard to explain, call it Pythonic and write a blog post.",
    "If the implementation is easy to explain, rename it three times and ship it in a hidden package.",
    "The only real way to write Python is to give up and do what the linter tells you."
]


if __name__ == "__main__":
    print("\nThe Zen of Spite — Dedicated to everyone who saw through the bullshit:\n")
    for line in spite_verses:
        print(f"• {line}")