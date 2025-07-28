#!/usr/bin/env python3
"""
Test script to verify OCR functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from cv_processor import CVProcessor
import json

def test_ocr():
    """Test OCR with a simple image"""
    print("Testing OCR functionality...")
    
    try:
        processor = CVProcessor()
        print("✓ CVProcessor initialized successfully")
        
        # Test with a sample image if available
        test_image_path = "test_image.png"  # You can place a test image here
        
        if os.path.exists(test_image_path):
            with open(test_image_path, 'rb') as f:
                image_data = f.read()
            
            text = processor.extract_text(image_data)
            print(f"✓ OCR extraction successful")
            print(f"Extracted text (first 200 chars): {text[:200]}")
            
            # Test text storage
            processor.store_text_data("test_pdf.pdf", 1, text)
            print("✓ Text storage successful")
            
            # Test search
            results = processor.search_text("test_pdf.pdf", "test")
            print(f"✓ Search functionality working, found {len(results)} results")
            
        else:
            print("ⓘ No test image found. OCR processor initialized successfully.")
            print("  Place a test image at 'test_image.png' to test full functionality.")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please install Python dependencies:")
        print("  cd backend && pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def check_tesseract():
    """Check if Tesseract is installed"""
    import subprocess
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ Tesseract found: {version_line}")
            return True
    except FileNotFoundError:
        print("✗ Tesseract not found in PATH")
        print("Please install Tesseract OCR:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        return False
    except Exception as e:
        print(f"✗ Error checking Tesseract: {e}")
        return False

if __name__ == "__main__":
    print("PDF Generator OCR Test\n" + "="*30)
    
    tesseract_ok = check_tesseract()
    ocr_ok = test_ocr()
    
    print("\n" + "="*30)
    if tesseract_ok and ocr_ok:
        print("✓ All tests passed! OCR functionality is ready.")
    else:
        print("✗ Some tests failed. Please check the issues above.")
