template = """#!/bin/bash
echo "Hello, {name}!"
"""


def build_sh_template(name: str) -> str:
    return template.format(name=name)
