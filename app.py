from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():

    return """

    <html>

    <body>

    <h1>Handwriting OCR</h1>

    <p>Server is running.</p>

    </body>

    </html>

    """