# slack-app-company-research

## これはなに？

企業名を slack で入力すると、その調査レポートが Notion に追加されるアプリ

### 使い方 v2025.02.07

インテグレーションに `company_research` が存在することを確認
> <img src="https://i.gyazo.com/2857a75666bf9b1b7cd7d6ceb0378a49.png">


<br/>チャンネルで `/research` コマンドを叩く
> <img src="https://i.gyazo.com/9e43d3a511585e74f4282d07dbf8464b.png">

<br/>モーダルが表示されるので、企業名と担当者名を入力する
> <img src="https://i.gyazo.com/c0249552ecc3b525f8894ba58620b3cb.png">


<br/>`#neox_sales_企業リサーチ` チャンネルにメッセージが送信される
> <img src="https://i.gyazo.com/6920bd97ac17a1bbebbbb93acb3166c8.png">

## 開発

```bash
$ git clone git@github.com:algomatic-inc/slack-app-company-research.git
$ cd slack-app-company-research
$ uv sync
```

### デプロイ

```bash
$ cp .chalice/config-base.json .chalice/config.json
# .chalice/config.json の環境変数を設定
$ uv pip compile pyproject.toml -o requirements.txt
$ uv run chalice deploy
```

chalice deploy を実行すると以下のように表示される
```
uv run chalice deploy
Creating shared layer deployment package.
  Reusing existing shared layer deployment package.
Creating app deployment package.
Updating lambda layer: [関数名]-managed-layer
Updating policy for IAM role: [関数名]-api_handler
Updating lambda function: [関数名]
Updating rest API
Resources deployed:
  - Lambda Layer ARN: arn:aws:lambda:ap-northeast-1:***:layer:[関数名]-managed-layer:56
  - Lambda ARN: arn:aws:lambda:ap-northeast-1:***:function:[関数名]
  - Rest API URL: https://***.execute-api.ap-northeast-1.amazonaws.com/api/
```

Rest API URL は slack アプリの設定で使用するので控えておく


## 開発準備

環境変数は `.chalice/config.json` で設定している

```json
{
  "version": "2.0",
  "app_name": "recruta-gtm-dev-company-research",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "SLACK_BOT_APP_ID": "A08BH6APPE0",
        "SLACK_BOT_TOKEN": "xoxb-***",
        "SLACK_SIGNING_SECRET": "",
        "SLACK_CLIENT_ID": "5046901820945.8391214805476",
        "SLACK_CLIENT_SECRET": "",
        "SLACK_REDIRECT_URI": "https://***.execute-api.ap-northeast-1.amazonaws.com/api/slack/oauth_redirect",
        "SLACK_INSTALL_PATH": "https://***.execute-api.ap-northeast-1.amazonaws.com/api/slack/install",
        "SLACK_SCOPES": "app_mentions:read,channels:history,chat:write,commands,users:read",
        "SLACK_INSTALLATION_S3_BUCKET_NAME": "recruta-gtm-dev-slack-installations",
        "SLACK_STATE_S3_BUCKET_NAME": "recruta-gtm-dev-slack-slate-store",
        "SLACK_WORKFLOW_CHANNEL_ID": "C08CC1WBVPE",
        "OPENAI_API_KEY": "sk-proj-***",
        "PERPLEXITY_API_KEY": "pplx-***",
        "NOTION_API_KEY": "ntn_***",
        "NOTION_DATABASE_ID": "***"
      },
      "autogen_policy": false,
      "automatic_layer": true
    }
  },
  "lambda_timeout" : 300,
  "exclude": [
    ".env"
  ]
}
```

### slack アプリの設定

[api.slack.com/apps](https://api.slack.com/apps) でアプリを作成（画像中に表示されているアプリ [商談企業リサーチ](https://api.slack.com/apps/A08BH6APPE0/general?) アプリ）

以下のページから `` を設定
> <img src="https://i.gyazo.com/dc6b04fa6ef90b8e041d60d3a6af5c9b.png">

以下のページから OAuth Token を取得し `SLACK_BOT_TOKEN` に設定し、`Reinstall in Algomatic` をクリック
> <img src="https://i.gyazo.com/78952633b38fc98e48dafae4320f5f27.png">

#### Slash Command

slack から `/research` コマンドを叩いて実行するため slash command を設定する

> <img src="https://i.gyazo.com/b23cfb108596fd3df5bc1418970c6b24.png">

Request URL には `chalice deploy` を実行した後に表示される Rest API URL を用いて `{REST_API_URL}/slack/events` を設定する

#### OAuth & Permissions

Scopes に以下を設定

```txt
app_mentions:read
channels:history
chat:write
commands
users:read
groups:history
files:read
```

#### Event Subscriptions

`On` に設定し、Request URL に `{REST_API_URL}/slack/events` を設定

また Subscribe to bot events に以下を設定

```txt
app_mention
message.channels
message.groups
file_shared
```

#### Install App

設定後、`Reinstall to Algomatic` をクリック
> <img src="https://i.gyazo.com/78952633b38fc98e48dafae4320f5f27.png">

また、`{REST_API_URL}/slack/install` にアクセスしてインストールを行う
> <img src="https://i.gyazo.com/f40cc267cd241184b0b312f8e973ffa4.png">

### Notion の設定

[インテグレーション](https://www.notion.so/profile/integrations) を事前に作成し、APIキーを `NOTION_API_KEY` に設定

Notion DB の ID を取得して `NOTION_DATABASE_ID` に設定（このDBに調査結果が保存される）
> <img src="https://i.gyazo.com/4a1f2739de7400d10750a86aeed45180.png">

<br/>ページ右上の設定から `接続` を開き、作成したインテグレーション（ここでは `neox-utility`）を選択
> <img src="https://i.gyazo.com/4250b33cd1dfb0f210890e7c288301fb.png">

### AWS環境

Lambda のタイムアウト（`lambda_timeout`）を実行時間以上に設定
> <img src="https://i.gyazo.com/64053e0573a87d3310949db50833f9ba.png">

#### S3

以下の名前のOAuth認証用のバケットを作成して `.chalice/config.json` に設定 [[参考]([text](https://dev.classmethod.jp/articles/aws-chalice-slack-app-bolt-for-python/))]

```yaml
"SLACK_INSTALLATION_S3_BUCKET_NAME": "recruta-gtm-dev-slack-installations"
"SLACK_STATE_S3_BUCKET_NAME": "recruta-gtm-dev-slack-slate-store"
```

### その他

- [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) から API キーを取得
