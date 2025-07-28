# PDF Generator Setup Instructions

## OCR Setup Requirements

This project uses OCR (Optical Character Recognition) to extract text from uploaded images, making the generated PDFs searchable.

### Prerequisites

1. **Tesseract OCR** - Required for text extraction from images
2. **Python 3.7+** - For the backend OCR processing
3. **Node.js** - For the main application

### Installation Steps

#### 1. Install Tesseract OCR

**On macOS (using Homebrew):**

```bash
brew install tesseract
```

**On Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**On Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

#### 2. Verify Tesseract Installation

```bash
tesseract --version
```

#### 3. Set up the project

```bash
# Make the startup script executable
chmod +x start.sh

# Run the full setup
./start.sh
```

### Manual Setup (Alternative)

If the automatic script doesn't work:

#### Backend Setup:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python server.py
```

#### Frontend Setup (in a new terminal):

```bash
npm install
npm start
```

### Usage

1. Access the application at `http://localhost:3000`
2. Upload images (JPG, PNG supported)
3. Drag and drop to reorder images
4. Click "Convert to PDF"
5. The system will:
   - Generate a PDF from your images
   - Extract text from each image using OCR
   - Store the text data for searching
6. Use the search box to find specific words or phrases in your PDF
7. Download your searchable PDF

### Features

- **Image to PDF Conversion**: Convert multiple images into a single PDF
- **OCR Text Extraction**: Automatically extract text from images using Tesseract
- **Full-Text Search**: Search for any word or phrase in your generated PDF
- **Drag & Drop Reordering**: Arrange images in any order before conversion
- **CV/Resume Analysis**: Special processing for CV/resume documents with scoring

### Troubleshooting

**Tesseract not found error:**

- Make sure Tesseract is installed and in your system PATH
- On macOS, try: `brew install tesseract`
- Verify with: `tesseract --version`

**Python backend not starting:**

- Check if port 56948 is available
- Ensure all Python dependencies are installed
- Activate the virtual environment before running

**Search not working:**

- Make sure the Python backend is running on port 56948
- Check browser console for any JavaScript errors
- Verify that text extraction completed after PDF generation
