from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your React dev server (localhost:3000) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Soccer Evolved API is running"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # We ignore the file for now and return a fake score
    return {"competence": 0.75}
