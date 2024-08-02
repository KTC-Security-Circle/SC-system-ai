import logging
from sc_system_ai.logging_config import setup_logging

from typing import Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool


logger = logging.getLogger(__name__)

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
        logger.info(f"Magic Function Toolが次の値で呼び出されました: {input}")
        return input + 2
    

magic_function = MagicFunctionTool()

if __name__ == "__main__":
    print(magic_function.invoke({"input": 3}))