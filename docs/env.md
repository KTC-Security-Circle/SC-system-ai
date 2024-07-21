# .envの設定方法

.envファイルは、アプリケーションの環境変数を格納するために使用されます。これらの変数は、Azure OpenAIのエンドポイント、APIキー、デプロイメント名など、アプリケーションのさまざまな設定に使用することができます。

以下の手順に従って、.envファイルを設定します。

1. プロジェクトディレクトリ内に新しいファイルを作成し、`.env`という名前を付けます。

2. テキストエディタで`.env`ファイルを開きます。

3. 必要なパラメータをファイルに追加します。各パラメータは新しい行に記述し、`KEY=VALUE`の形式で記述します。例:

    ```
    AZURE_OPENAI_ENDPOINT=''
    AZURE_OPENAI_API_KEY=''
    AZURE_DEPLOYMENT_NAME=''
    AZURE_EMBEDDINGS_DEPLOYMENT_NAME=''
    OPENAI_API_VERSION=''
    ```

    一般的なパラメータの例:

    - `AZURE_OPENAI_ENDPOINT`: Azure OpenAIのエンドポイント。
    - `AZURE_OPENAI_API_KEY`: Azure OpenAIのAPIキー。
    - `AZURE_DEPLOYMENT_NAME`: Azure OpenAI Chaiモデルのデプロイメント名。
    - `AZURE_EMBEDDINGS_DEPLOYMENT_NAME`: Azure OpenAI Embeddingsモデルのデプロイメント名。
    - `OPENAI_API_VERSION`: Azure OpenAIのAPIバージョン。

    **Azure OpenAIについては[こちら](azure-openai.md)から**

4. `.env`ファイルを保存します。

5. `.env`ファイルをプロジェクトの`.gitignore`ファイルに追加して、バージョン管理システムにコミットされないようにします。

6. Pythonのアプリケーションのコードでは、`python-dotenv`パッケージを使用して`.env`ファイルから変数を読み込むことができます。

    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv()

    azureOpenAIEndpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azureOpenAIKey = os.getenv('AZURE_OPENAI_API_KEY')
    azureDeploymentName = os.getenv('AZURE_DEPLOYMENT_NAME')
    azureEmbeddingsDeploymentName = os.getenv('AZURE_EMBEDDINGS_DEPLOYMENT_NAME')
    openAIApiVersion = os.getenv('OPENAI_API_VERSION')
    ```

    必要なパッケージやライブラリをインストールして、特定のプログラミング言語やフレームワークで環境変数を使用できるようにしてください。Pythonでは、`python-dotenv`パッケージをインストールする必要があります。これは、以下のコマンドでインストールできます。

    ```bash
    pip install python-dotenv
    ```

以上で、.envファイルの設定が完了し、アプリケーションで環境変数を使用できるようになります。