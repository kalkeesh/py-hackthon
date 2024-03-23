from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/hackathon-data")
async def get_excel_data():
    file_path = "Hackathon.xlsx"
    try:
        df = pd.read_excel(file_path)
        data = df.to_dict(orient="records")
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})