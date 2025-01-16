# DocumentFormatter

`CosmosDBManager`クラスからドキュメントを追加する場合`src/sc_system_ai/template/document_formatter.py`の関数群を使用します。

## 基本動作

テキストを分割する関数は、文章を1000文字程度で分割します。この大きさは引数`chunk_size`、`chunk_overlap`から指定可能です。

以下のメタデータを付与します。

- created_at : 作成日時
- updated_at : 更新日時

### `md_formatter()`

#### 引数

| 引数名         | 型                | 説明                           |
|----------------|-------------------|--------------------------------|
| `text`         | str               | Markdown形式のテキスト         |
| `title`        | str (optional)    | タイトル                       |
| `metadata`     | dict[str, Any] (optional) | メタデータ             |
| `chunk_size`   | int (optional)    | 分割するサイズ                 |
| `chunk_overlap`| int (optional)    | オーバーラップのサイズ         |

#### 動作

マークダウン形式のテキストを分割し、メタデータを付与します。
`Document`オブジェクトを返却します。
メタデータにはヘッダーが付与されています。

テキストの分割はヘッダー毎に行います。
分割したテキストがチャンクサイズを超える場合また分割を行います。
2度目の分割を行ったテキストにはセクション番号がメタデータとして付与されます。

`title`を与えず呼び出した場合、対応するヘッダーをタイトルとしてメタデータに与えます。
ヘッダーがない場合は分割後のテキストの最初のテキストをタイトルとします。

### `text_formatter()`

#### 引数

| 引数名         | 型                | 説明                           |
|----------------|-------------------|--------------------------------|
| `text`         | str               | テキスト                       |
| `title`        | str (optional)    | タイトル                       |
| `metadata`     | dict[str, Any] (optional) | メタデータ             |
| `separator`    | str (optional)    | 区切り文字                     |
| `chunk_size`   | int (optional)    | 分割するサイズ                 |
| `chunk_overlap`| int (optional)    | オーバーラップのサイズ         |

#### 動作

セパレータとチャンクサイズで分割を行い、メタデータを付与します。

`title`を与えず呼び出した場合、分割後のテキストの最初のテキストをタイトルとします。

## `CosmosDBManager`での動作

`create_document`メソッドでベクターストアにドキュメントを作成します。

`updata_document`メソッドではメタデータ`updated_at`の更新を行います。
