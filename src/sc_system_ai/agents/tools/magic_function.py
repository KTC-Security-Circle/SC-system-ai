from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

from sc_system_ai.logging import logger

class MagicFunctionInput(BaseModel):
    input: int = Field(description="Input value for magic function")


@tool("magic_function_tool", args_schema=MagicFunctionInput)
def magic_function(input: int) -> int:
    """Applies a magic function to an input."""
    logger.info(f"Applying magic function to input: {input}")
    return input + 2