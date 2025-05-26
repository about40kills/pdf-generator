from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from cv_processor import CVProcessor
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdf-generator-61cx.onrender.com",
                   "http://localhost:3000"], 
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
    

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...), pdf_name: str = None, page_number: int = None):
    try:
        contents = await file.read()
        text = cv_processor.extract_text(contents)

        print(f"Extracted text (first 100 chars): {text[:100]}")
        
        if pdf_name and page_number is not None:
            cv_processor.store_text_data(pdf_name, page_number, text)
            print(f"Stored text for {pdf_name}, page {page_number}")
        
        return {"text": text}
    except Exception as e:
        print(f"Error extracting text: {e}")
        return {"error": str(e)}

@app.get("/search")
async def search_text(pdf_name: str, query: str):
    try:
        print(f"Searching for '{query}' in {pdf_name}")
        results = cv_processor.search_text(pdf_name, query)
        print(f"Search results: {results}")
        return {"results": results}
    except Exception as e:
        print(f"Error searching: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=56948)