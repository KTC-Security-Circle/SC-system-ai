# Agentの作り方について

## 目次

- [Agentの作り方について](#agentの作り方について)
  - [目次](#目次)
  - [概要](#概要)
  - [1. 基底クラスAgentの定義](#1-基底クラスagentの定義)
    - [クラス概要](#クラス概要)
    - [属性](#属性)
    - [メソッド](#メソッド)
  - [2. `MyAgent`クラスの定義](#2-myagentクラスの定義)
    - [クラス概要](#クラス概要-1)
    - [属性](#属性-1)
    - [メソッド](#メソッド-1)
  - [3. 使用例](#3-使用例)
    - [エージェントの作成と実行](#エージェントの作成と実行)
  - [4. 実行結果](#4-実行結果)


## 概要

この説明書は、Agentクラスの基底クラスと、そのサブクラスであるMyAgentクラスの作成方法を解説します。特に、共通の変数、サブクラスごとに変更される変数、およびインスタンス作成時に登録される変数について詳しく説明します。

## 1. 基底クラスAgentの定義

### クラス概要

`Agent`クラスは、エージェントの情報を保持し、エージェントを実行するための基底クラスです。このクラスは、共通のツールやエージェント情報を提供します。

### 属性

- `llm` (`AzureChatOpenAI`): OpenAIのモデル。デフォルトは`llm`。
- `user_info` (`User`): ユーザー情報。デフォルトは`User()`。
- `assistant_info` (`str`): 各エージェントで設定するアシスタント情報。
- `tools` (`List`): エージェントが使用するツール。デフォルトは共通のツールリスト。
- `full_prompt` (`PromptTemplate`): 完全なプロンプトテンプレート。
- `agent_info` (`str`): エージェント情報のフォーマット。

### メソッド

- `__init__(self, llm: AzureChatOpenAI = llm, user_info: User = User())`: コンストラクタ。インスタンス変数の初期化を行う。
- `set_tools(self, tools)`: ツールを追加する関数。
- `invoke(self, message: str)`: エージェントを実行する関数。
- `get_agent_info(self)`: エージェント情報を取得する関数。

```python
class Agent:
    def __init__(self, llm: AzureChatOpenAI = llm, user_info: User = User()):
        self.llm = llm
        self.user_info = user_info
        self.assistant_info = None
        self.tools = template_tools
        self.full_prompt = PromptTemplate(assistant_info=self.assistant_info, user_info=self.user_info)
        self.get_agent_info()

    def set_tools(self, tools):
        self.tools += tools
    
    def invoke(self, message: str):
        agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=self.full_prompt.full_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        try:
            logger.info("エージェントの実行を開始します。\n-----------\n")
            result = agent_executor.invoke({
                "chat_history": self.user_info.conversations.format_conversation(),
                "messages": message, 
                })
        except Exception as e:
            logger.error(f"エージェントの実行に失敗しました。エラー内容: {e}")
            result = "エージェントの実行に失敗しました。"
        return result
    
    def get_agent_info(self):
        self.agent_info = agent_info.format(
            assistant_info=self.assistant_info,
            user_info=self.user_info,
            tools=self.tools
        )
        return self.agent_info
```

## 2. `MyAgent`クラスの定義

### クラス概要

`MyAgent`クラスは、`Agent`クラスを継承し、サブクラスごとに変更される変数とインスタンス作成時に登録される変数を初期化します。

### 属性

- `additional_variable` (`str`): サブクラス固有の追加変数。

### メソッド

- `__init__(self, llm: AzureChatOpenAI = llm, user_info: User = User(), additional_variable: str)`: コンストラクタ。基底クラスのコンストラクタを呼び出し、追加変数を初期化する。
- `display_info(self)`: エージェント情報を表示する関数。

```python
class MyAgent(Agent):
    def __init__(self, llm: AzureChatOpenAI = llm, user_info: User = User(), additional_variable: str):
        super().__init__(llm=llm, user_info=user_info)
        self.assistant_info = "サブクラスのアシスタント情報"
        self.additional_variable = additional_variable
        super().set_tools([magic_function])
    
    def display_info(self):
        print(self.get_agent_info())
        print(f"追加の変数: {self.additional_variable}")
```

## 3. 使用例

### エージェントの作成と実行

```python
if __name__ == "__main__":
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    history = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(history)

    # エージェントの作成
    my_agent = MyAgent(user_info=user_info, additional_variable="特別な情報")
    
    # エージェントの情報を表示
    my_agent.display_info()
    
    # エージェントの実行
    result = my_agent.invoke("magic function に３をいれて")
    print(result)
```

## 4. 実行結果
```bash
エージェント情報:
-------------------
    assistant_info: サブクラスのアシスタント情報
    user_info: name: hogehoge, major: fugafuga専攻, conversation: [('human', 'こんにちは!'), ('ai', '本日はどのようなご用件でしょうか？')]
    tools: [DuckDuckGoSearchRun(), MagicFunctionTool()]
-------------------
エージェントの実行を開始します。
-------------------
結果: (エージェントの実行結果)
```