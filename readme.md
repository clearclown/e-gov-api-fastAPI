# 🚀 FastAPIを使用したe-Gov APIプロジェクトの詳細ガイド 🌐

## プロジェクトの概要
このプロジェクトは、FastAPIフレームワークを使用して、e-Gov APIにアクセスし、公的文書を取得するためのAPIを構築することを目的としています。プロジェクトには、Dockerfile、必要なPythonパッケージを指定したrequirements.txt、FastAPIアプリケーションのメインスクリプト、そしてテンプレートを含むHTMLファイルが含まれています。

### 📝 8.1 files.txtを分析する
各ファイルの内容を確認し、全体の構成を把握します。

### 📝 8.2 タイトルを決める
**タイトル:** "🚀 FastAPIを使用したe-Gov APIプロジェクトの詳細ガイド 🌐"

### 📝 8.3 プロジェクトの概要
このプロジェクトは、FastAPIフレームワークを使用して、e-Gov APIにアクセスし、公的文書を取得するためのAPIを構築することを目的としています。プロジェクトには、Dockerfile、必要なPythonパッケージを指定したrequirements.txt、FastAPIアプリケーションのメインスクリプト、そしてテンプレートを含むHTMLファイルが含まれています。

### 📝 8.4 各種バージョン、動作環境
- **Python:** 3.10-slim
- **FastAPI:** 最新バージョン
- **httpx:** 最新バージョン
- **uvicorn:** 最新バージョン

### 📝 8.5 仕様技術を表にてまとめる
| 技術       | バージョン    |
|------------|---------------|
| Python     | 3.10-slim     |
| FastAPI    | 最新          |
| httpx      | 最新          |
| uvicorn    | 最新          |
| Docker     | 最新          |

### 📝 8.6 仕様技術の説明をする。
- **Python:** オブジェクト指向の高レベルプログラミング言語であり、読みやすさと生産性の高さが特徴です。
- **FastAPI:** 高速なAPIを構築するためのPythonフレームワークで、簡単に使えると同時に非常にパフォーマンスが高いです。まるで光速でデータを取得できるような感覚を味わえます🚀。Djangoは古典的な映画のように堅実で信頼できますが、FastAPIは最新のSF映画のようにスピーディでスタイリッシュです。
- **httpx:** HTTPリクエストを行うための非同期クライアントです。非同期処理により、他のタスクをブロックせずにHTTPリクエストを送信できます。
- **uvicorn:** FastAPIアプリケーションを実行するためのASGIサーバーです。高性能なASGIサーバーとして知られています。
- **Docker:** アプリケーションをコンテナ内で実行するためのプラットフォームで、一貫性のある環境を提供します。コンテナ化により、依存関係の問題を解消し、デプロイが容易になります。

### 📝 8.7 ディレクトリ構成をまとめる
```
e-gov-api-fastAPI/
├── Dockerfile
├── requirements.txt
└── app/
    ├── main.py
    └── templates/
        └── index.html
```

### 📝 8.8 各ファイルの関数がどこのファイルに接続するかを矢印にて詳細とともに説明をする。
- **main.py**
  - `read_root` 関数: `index.html`テンプレートを返す。
  - `get_official_document` 関数: e-Gov APIにPOSTリクエストを送信し、結果を`index.html`テンプレートに渡す。

### 📝 8.9 各ファイルの重要な部分の説明をする。
- **Dockerfile:** Pythonのスリムなイメージを使用してアプリケーションをコンテナ化します。これにより、軽量で効率的なコンテナイメージを作成できます。
- **requirements.txt:** FastAPI、httpx、uvicornなどの依存関係を指定します。これにより、環境の一貫性が保たれます。
- **main.py:** FastAPIアプリケーションのメインスクリプトです。APIエンドポイントの定義と、e-Gov APIとの通信を行います。
- **index.html:** 公的文書を取得するためのフォームを含むHTMLテンプレートです。ユーザーインターフェースを提供します。

### 📝 8.10 各ファイルの詳細な説明
**main.py**
```python
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

class OfficialDocumentRequest(BaseModel):
    arrive_id: str
    notice_sub_id: int

class Metadata(BaseModel):
    title: str
    detail: str
    type: str
    instance: str

class Result(BaseModel):
    arrive_id: str
    notice_sub_id: int
    proc_name: str
    doc_title: str
    download_date: str
    file_name_list: list

class OfficialDocumentResponse(BaseModel):
    metadata: Metadata
    results: Result

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/official_document", response_class=HTMLResponse)
async def get_official_document(request: Request, arrive_id: str = Form(...), notice_sub_id: int = Form(...)):
    url = "https://api.example.com/official_document"  # 実際のAPIエンドポイントに変更
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_access_token",  # 実際のアクセストークンに変更
        "x-6eovAPI-Trial": "true"
    }
    payload = {"arrive_id": arrive_id, "notice_sub_id": notice_sub_id}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()  # HTTPステータスコードが200番台でない場合例外を発生
        document = response.json()
        return templates.TemplateResponse("index.html", {"request": request, "document": document})
    except httpx.HTTPStatusError as exc:
        error_message = f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error_message})
    except Exception as exc:
        error_message = f"An error occurred: {str(exc)}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error_message})
```

**index.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Official Document</title>
</head>
<body>
    <h1>Official Document</h1>
    <form action="/official_document" method="post">
        <label for="arrive_id">Arrive ID:</label>
        <input type="text" id="arrive_id" name="arrive_id" required>
        <br>
        <label for="notice_sub_id">Notice Sub ID:</label>
        <input type="number" id="notice_sub_id" name="notice_sub_id" required>
        <br>
        <button type="submit">Get Document</button>
    </form>
    {% if document %}
    <h2>Document Details</h2>
    <pre>{{ document }}</pre>
    {% endif %}
</body>
</html>
```

### 📝 8.11 実行方法を記す
1. リポジトリをクローンします。
2. Dockerを使用してアプリケーションをビルドし、実行します。
   ```bash
   docker build -t e-gov-api-fastapi .
   docker run -d -p 8001:8001 e-gov-api-fastapi
   ```
3. ブラウザで `http://localhost:8001` にアクセスし

、公的文書を取得するためのフォームに必要な情報を入力して送信します。

---

## 追加点
- **FastAPIの利点:** FastAPIは、非常に高速で、開発者にとって使いやすいです。他のフレームワーク、例えばDjangoやFlaskに比べて、非同期機能が組み込みでサポートされているため、パフォーマンスが向上します。
- **Flaskとの比較:** Flaskは軽量で、シンプルなアプリケーションを迅速に開発するのに適していますが、FastAPIはより高速で、データバリデーションとシリアル化のためのPydanticを活用することができます。
- **バックエンドとは:** バックエンドは、アプリケーションのサーバー側の部分で、データベースとのやり取りや、ビジネスロジックの実行を担当します。このプロジェクトでは、FastAPIがバックエンドとして機能し、e-Gov APIとの通信を行います。

---

### 👨‍🏫 豆知識
- **Django:** Pythonで最も人気のあるフレームワークの一つで、大規模なウェブアプリケーションに適しています。豊富な機能が標準で提供されています。
- **Flask:** 軽量なマイクロフレームワークで、簡単に拡張できるのが特徴です。シンプルなアプリケーションに適しています。
- **バックエンド開発:** クライアントサイド（フロントエンド）からのリクエストを処理し、必要なデータを提供する役割を担います。サーバー、データベース、アプリケーションロジックを含みます。

