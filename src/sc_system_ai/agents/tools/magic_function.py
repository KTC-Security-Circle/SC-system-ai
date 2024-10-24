import logging

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MagicFunctionInput(BaseModel):
    input: int = Field(description="Input value for magic function")


class MagicFunctionTool(BaseTool):
    name: str = "magic_function_tool"
    description: str = "Applies a magic function to an input."
    args_schema: type[BaseModel] = MagicFunctionInput

    def _run(
            self,
            input: int,
    ) -> int:
        """use the tool."""
        logger.info(f"Magic Function Toolが次の値で呼び出されました: {input}")
        logger.debug(f"Magic Function Toolが次の値で呼び出されました: {input}")
        return input + 2


magic_function = MagicFunctionTool()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    print(magic_function.invoke({"input": 3}))
