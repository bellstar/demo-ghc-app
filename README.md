# Azure OpenAI Console App Template

Azure OpenAI にアクセスするための、Python と Microsoft Agent Framework ベースのコンソールアプリひな型です。

## Requirements

- Python 3.12 以降
- Azure OpenAI リソースとチャットモデルのデプロイ
- Azure CLI でのサインイン、または Azure OpenAI API キー

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

`.env.example` を `.env` にコピーし、Azure OpenAI の設定値を入力します。

```powershell
Copy-Item .env.example .env
```

Microsoft Entra ID 認証を使う場合は、Azure CLI でサインインします。

```powershell
az login
```

`AZURE_OPENAI_API_KEY` を設定した場合は、キー認証を使用します。

## Run

```powershell
demo-ghc-app
```

プロンプトを入力して Enter キーを押します。終了するには `exit`、`quit`、または `q` を入力します。

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI エンドポイント。例: `https://<resource>.openai.azure.com` |
| `AZURE_OPENAI_CHAT_MODEL` | Yes | Azure OpenAI のチャットモデルデプロイ名 |
| `AZURE_OPENAI_API_VERSION` | No | Azure OpenAI API バージョン。省略時は Agent Framework プロバイダーの既定動作に従います。 |
| `AZURE_OPENAI_API_KEY` | No | 任意の API キー。省略時は Azure CLI 資格情報を使用します。 |
| `AGENT_NAME` | No | エージェント名。既定値は `AzureOpenAIConsoleAgent` です。 |
| `AGENT_INSTRUCTIONS` | No | エージェントに与えるシステム指示です。 |
