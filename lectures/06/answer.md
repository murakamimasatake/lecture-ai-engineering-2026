# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要'})
aws_aws___read_documentation({'requests': [{'url': 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html'}]})

- 気づき・疑問：
ローカルで動かした自作サーバー（uv）、公開パッケージを都度取得して動かすサーバー（uvx）、外部のクラウド上で動いているサーバー（url）の3種類すべてを、app/mcp_servers.json に接続先を書き足すだけでエージェントから同じ形式で扱える点に MCP の汎用性を感じた。また、STEP 4 ではモデルが自律的に「まず search_documentation で検索し、次に read_documentation で詳細ページを読む」という2段階のツール呼び出しを組み立てており、説明文の設計がモデルの行動に直結していることがよく分かった。

今回のように複数の MCP サーバーを同時に接続すると、モデルに渡るツール数が増える（今回は7個）が、実務でさらに多くのサーバーを繋いだ場合、プロンプトのトークン消費量やツールの選択精度にどの程度影響が出るのか、またツール数が多くなった際の絞り込み方や管理のベストプラクティスが気になった。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：`app/mcp_server.py` の TODO の下に `server.tool()(tools.get_lecture_summary)` を1行書き足して保存し、エージェント側のコードや設定を変えずにツール一覧と質問応答を確認した。
- 結果：`uv run python -m app.mcp_agent --list-tools` で `glossary_get_lecture_summary` が増えていることを確認し、「第2回では何を学びますか?」の質問に対して `[tool call] glossary_get_lecture_summary({'lecture': 2})` が呼ばれて回答が返ることを確認した。
- 気づき・疑問：エージェント起動時に MCP サーバーへツール一覧を問い合わせる仕組みのため、サーバー側で公開する関数を1行増やすだけでクライアント側の改修なしに機能拡張できることを確認できた。
