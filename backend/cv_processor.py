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
        #convert bytes into numpy array
        nparr = np.frombuffer(image_data, np.unit8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        #convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        #apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        #denoise using median blur
        denoised = cv2.fastNlMeansDenoising(thresh)
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


