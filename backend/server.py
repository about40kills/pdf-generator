from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from cv_processor import CVProcessor
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdf-generator-61cx.onrender.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#initialize Cv processor
cv_processor = CVProcessor()

@app.post("/process-cv")
async def process_cv(file: UploadFile = File(...)):
    try:
        #read the upload file
        contents = await file.read()

        #process the cv
        result = cv_processor.process_cv(contents)


        return result
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)