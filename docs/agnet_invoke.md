# invokeメソッドの挙動

`invoke()`メソッドはエージェントの実行を行います。
ストリーミングレスポンスに対応するためにジェネレータとして定義されています。
エージェントが回答の生成を終えてからレスポンスを受け取ることも可能です。

## ストリーミング有効

以下のようにしてレスポンスを受け取ることができます。

```python
for resp in agent.invoke(messgae):
    print(message)
```

関数として実装する場合、以下のようにすることも可能です。

```python
def main(message):
    yield from agent.invoke(message)
```

エージェントのインスタンス化時にreturn_lengthで指定した長さ以上の文字数で返却されます。
デフォルトでは5になっています。

```bash
こんにちは!
何かお手伝
いできるこ
とはありま
すか？
```

ストリーミングでの取得後、レスポンスの全体が必要な場合は`get_response()`メソッドを使用してください。

```python
print(agent.get_response())
```

## ストリーミング無効

ストリーミングはデフォルトで有効になっているため、インスタンス化の際に無効化する必要があります。

```python
agent = Agent(
    user_info=user_info,
    is_streaming=False
)
```

`invoke()`メソッドはジェネレータとして実装されているため、`next()`関数を使用し呼び出してください。

```python
print(next(agent.invoke(message)))
```

実行結果は以下のようになります。

```bash
{'chat_history': [chat_history], 'messages': 'こんにちは', 'output': 'こんにちは!何かお手伝いできることはありますか？'}
```
