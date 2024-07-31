from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from sc_system_ai.template.prompts import assistant_info_template, full_system_template
from sc_system_ai.template.user_prompts import UserPromptTemplate, User

class PromptTemplate:
    def __init__(
            self, 
            full_system_template: str = full_system_template,
            assistant_info: str = assistant_info_template, 
            user_info: str = User,
            ):
        self.full_system_template = full_system_template
        self.assistant_info = assistant_info
        self.user_info = user_info

        self.user_info_prompt = UserPromptTemplate(user_info=self.user_info)

        self.full_prompt = self.create_prompt(assistant_info=self.assistant_info, user_info=self.user_info)
    
    def __str__(self):
        return self.full_prompt

    def create_prompt(self, assistant_info: str = None, user_info: str = None):
        """フルのシステムプロンプトを作成する関数"""
        formatted_system_prompt = self.full_system_template.format(assistant_info=assistant_info, user_info=self.user_info_prompt)
        self.full_prompt = ChatPromptTemplate.from_messages([
            ("system", formatted_system_prompt), # システムプロンプト
            ("placeholder", "{chat_history}"),  # ユーザーとの会話
            ("human", "{messages}"), 
            ("placeholder", "{agent_scratchpad}"),
        ])
        return self.full_prompt
    
    def get_prompt(self):
        return self.full_prompt.messages

    def show_prompt(self):
        print(f'prompts: {self.full_prompt.messages} \ninput_variables: {self.full_prompt.input_variables}')



if __name__ == "__main__":
    user = User(name="yuki", major="スーパーAIクリエイター専攻")
    print(user)
    prompt = PromptTemplate(user_info=user)
    print(prompt.full_prompt)