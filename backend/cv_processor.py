import cv2 
import numpy as np
import pytesseract
import spacy
from PIL import Image
from typing import Dict, List, Tuple
import io


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

    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise Exception("Could not decode image")

        # Resize for better OCR - scale up small images
        height, width = img.shape[:2]
        if width < 1000 or height < 1000:
            scale_factor = max(1000/width, 1000/height, 2.0)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Noise reduction
        denoised = cv2.medianBlur(thresh, 3)
        
        # Deskewing for better OCR accuracy
        try:
            # Get skew angle
            coords = np.column_stack(np.where(denoised > 0))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                
                # Rotate if skew is significant
                if abs(angle) > 0.5:
                    (h, w) = denoised.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    denoised = cv2.warpAffine(denoised, M, (w, h),
                                         flags=cv2.INTER_CUBIC,
                                         borderMode=cv2.BORDER_CONSTANT, 
                                         borderValue=255)
        except Exception as e:
            print(f"Deskewing failed: {e}")
            # Continue without deskewing
        
        return denoised
    
    def extract_text(self, image_data: bytes) -> str:
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_data)

            # Multiple OCR configurations for better results
            configs = [
                r'--oem 3 --psm 6 -l eng',  # Default config
                r'--oem 3 --psm 3 -l eng',  # Fully automatic page segmentation
                r'--oem 3 --psm 1 -l eng',  # Automatic page segmentation with OSD
                r'--oem 3 --psm 11 -l eng', # Sparse text
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    # Extract text with confidence scores
                    text = pytesseract.image_to_string(processed_image, config=config)
                    
                    # Get confidence data
                    data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Use the result with highest confidence and reasonable text length
                    if avg_confidence > best_confidence and len(text.strip()) > 10:
                        best_text = text
                        best_confidence = avg_confidence
                        
                except Exception as e:
                    print(f"OCR config failed: {config}, error: {e}")
                    continue
            
            # If no good result, use the first config as fallback
            if not best_text.strip():
                best_text = pytesseract.image_to_string(processed_image, config=configs[0])
            
            # Clean up the text
            best_text = self.clean_extracted_text(best_text)
            
            # Debug logging
            print(f"Extracted text length: {len(best_text)}")
            print(f"Text sample: {best_text[:200]}")
            print(f"Best confidence: {best_confidence}")
            
            return best_text
        except Exception as e:
            print(f"OCR error: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")
        
    def clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                # Remove multiple spaces
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        

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


