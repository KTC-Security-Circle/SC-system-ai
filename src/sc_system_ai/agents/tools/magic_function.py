from typing import Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from sc_system_ai.logging import logger

class MagicFunctionInput(BaseModel):
    input: int = Field(description="Input value for magic function")


class MagicFunctionTool(BaseTool):
    name = "magic_function_tool"
    description = "Applies a magic function to an input."
    args_schema: Type[BaseModel] = MagicFunctionInput
    
    def _run(
            self,
            input: int,
    ) -> int:
        """use the tool."""
        logger.info(f"Applying magic function to input: {input}")
        return input + 2
    

magic_function = MagicFunctionTool()