import cv2
import numpy as np
import pytesseract
import spacy
from PIL import Image
from typing import Dict, List, Tuple
import io
import json
import os


class CVProcessor:
    def __init__(self):
       #load English model for NLP
       self.nlp = spacy.load("en_core_web_sm")

       #cv related keywords for detection
       self.cv_keywords = ['experience', 'education', 'skills', 'projects', 'certificates and awards', 'resume',
                           'curriculum vitae', 'objective', 'summary', 'work history', 'cv', 'employment',
                           'contact' 'refrees', 'qualifications', 'achievements'
                           ]
       
       #cv scoring criteria
       self.scoring_criteria = {
           'experience': 30,
           'education':  20,
           'skills': 25,
           'contact': 10,
           'achievements': 15,
       }

       # Create a directory to store text data
       self.text_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
       if not os.path.exists(self.text_data_dir):
           os.makedirs(self.text_data_dir)

    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Resize for better OCR
        height, width = img.shape[:2]
        img = cv2.resize(img, (width*2, height*2), interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Less aggressive denoising
        denoised = cv2.medianBlur(thresh, 3)
        
        # Add deskewing
        try:
            # Get skew angle
            coords = np.column_stack(np.where(denoised > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Rotate if needed
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h),
                                     flags=cv2.INTER_CUBIC,
                                     borderMode=cv2.BORDER_CONSTANT, 
                                     borderValue=255)
        except:
            # Skip deskewing if it fails
            pass
        
        return denoised
    
    def extract_text(self, image_data: bytes) -> str:
        #extract text from the image using OCR
        try:
            #preprocess the image
            processed_image = self.preprocess_image(image_data)

            #perform OCR
            text = pytesseract.image_to_string(processed_image)
            return text
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
        

    def is_cv(self, text: str) -> bool:
        #Determine if the text is from a cv
        text_lower = text.lower()
        keyword_matches = sum(1 for keyword in self.cv_keywords
                              if keyword in text_lower)
        return keyword_matches >= 3
    
    def score_cv(self, text:str) -> Dict:
        #score cv based on its contents
        doc = self.nlp(text.lower())

        #define section keywords
        sections = {
            'education': ['education', 'degree', 'university', 'school', 'college',
                          'phd', 'bachelor', 'master'],
            'experience': ['experience', 'work', 'role', 'position', 'employment',
                           'job', 'intern'],
            'skills': ['skills', 'technical', 'proficiency', 'programming', 'languages', 
                       'expertise'],
            'contact': ['contact', 'email', 'phone', 'address', 'location', 'linkedin'], 
            'achievements': ['achievements', 'awards', 'accomplishments', 'projects', 'certifications']
        }

        score = 0
        section_scores = {}

        for section, keywords in sections.items():
            #check for keyword in presence
            section_present = any(keyword in text.lower()
                                  for keyword in keywords)
            if section_present:
                score += self.scoring_criteria[section] 

            section_scores[section] = {
                'present': section_present,
                'score': self.scoring_criteria[section] if section_present else 0
            }

        return {
            'total_score': score,
            'max_possible_score': sum(self.scoring_criteria.values()),
            'sections': section_scores
       }
        
    def  process_cv(self, image_data: bytes) -> Dict:
        #process a cv image and return analysis results
        text = self.extract_text(image_data)

        #check if it's a cv
        is_cv = self.is_cv(text)
        score = self.score_cv(text) if is_cv else None

        return{
            'is_cv': is_cv,
            'text': text,
            'score': score
        }

    def store_text_data(self, pdf_name: str, page_number: int, text: str):
        """Store extracted text data for a PDF page"""
        # Skip storage if text is empty
        if not text.strip():
            print(f"No text to store for {pdf_name}, page {page_number}")
            return
        
        data_file = os.path.join(self.text_data_dir, f"{pdf_name}.json")
        print(f"Storing text at: {data_file}")

        # Load existing data or create new
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"pages": {}}
        
        # Add new page data
        data["pages"][str(page_number)] = text
        
        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(data, f)

    def search_text(self, pdf_name: str, query: str) -> List[Dict]:
        """Search for text in a PDF and return matching pages"""
        data_file = os.path.join(self.text_data_dir, f"{pdf_name}.json")
        
        if not os.path.exists(data_file):
            return []
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        results = []
        query = query.lower()
        
        for page_num, text in data["pages"].items():
            if query in text.lower():
                # Get some context around the match
                text_lower = text.lower()
                start_idx = text_lower.find(query)
                context_start = max(0, start_idx - 50)
                context_end = min(len(text), start_idx + len(query) + 50)
                context = text[context_start:context_end]
                
                results.append({
                    "page": int(page_num),
                    "context": context,
                    "match": query
                })
        
        return results


