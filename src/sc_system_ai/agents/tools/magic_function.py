from langchain_core.tools import tool

# ツールの準備
@tool
def magic_function(input: int) -> int:
    """Applies a magic function to an input."""
    return input + 2