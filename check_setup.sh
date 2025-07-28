#!/bin/bash

echo "PDF Generator OCR Setup Check"
echo "=============================="

# Check if Tesseract is installed
echo "Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract found: $(tesseract --version | head -n1)"
else
    echo "✗ Tesseract not found"
    echo "  Install with: brew install tesseract (macOS) or sudo apt-get install tesseract-ocr (Ubuntu)"
fi

# Check if Python 3 is installed
echo ""
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 found: $(python3 --version)"
else
    echo "✗ Python 3 not found"
    echo "  Please install Python 3.7 or later"
fi

# Check if Node.js is installed
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    echo "✓ Node.js found: $(node --version)"
else
    echo "✗ Node.js not found"
    echo "  Please install Node.js from https://nodejs.org/"
fi

# Check if npm is installed
echo ""
echo "Checking npm..."
if command -v npm &> /dev/null; then
    echo "✓ npm found: $(npm --version)"
else
    echo "✗ npm not found"
    echo "  npm should come with Node.js installation"
fi

echo ""
echo "Next steps:"
echo "1. If any components are missing, install them first"
echo "2. Run: ./start.sh to set up and start the application"
echo "3. Or run: python3 test_ocr.py to test OCR functionality"
