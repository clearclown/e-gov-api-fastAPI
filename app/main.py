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
