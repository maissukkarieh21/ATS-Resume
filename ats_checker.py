import sys
import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from docx import Document
import pdfplumber

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')

# Load NLP tools
stop_words = set(stopwords.words('english'))
nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer()

# Read DOCX file
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Read PDF file
def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Clean text: Keep alphanumeric words and preserve tech keywords
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9+#.\-]', ' ', text)  # Keep programming terms like C++, C#, .NET
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip()

# Extract meaningful keywords
def extract_keywords(text):
    # Tokenize with spaCy
    doc = nlp(text)
    
    keywords = set()
    for token in doc:
        if token.is_stop or token.is_punct:  # Ignore stop words & punctuation
            continue
        lemma = lemmatizer.lemmatize(token.text)  # Convert to base form
        if len(lemma) > 1:  # Ignore single letters
            keywords.add(lemma)
    
    return keywords

# Check keyword match
def check_keywords(resume_text, job_description_text):
    job_keywords = extract_keywords(clean_text(job_description_text))
    print("job_keywords =>",job_keywords)
    resume_keywords = extract_keywords(clean_text(resume_text))
    
    matched_keywords = resume_keywords.intersection(job_keywords)

    return matched_keywords, len(matched_keywords), len(job_keywords)

# ATS Compatibility Check
def is_ats_friendly(file_path, job_description):
    resume_text = read_docx(file_path) if file_path.endswith(".docx") else read_pdf(file_path)
    
    matching_keywords, matched_keywords_count, total_keywords = check_keywords(resume_text, job_description)
    
    match_ratio = (matched_keywords_count / total_keywords) * 100 if total_keywords > 0 else 0

    return {
        "matched_keywords": list(matching_keywords),
        "matched_count": matched_keywords_count,
        "total_keywords": total_keywords,
        "score": round(match_ratio, 2),
        "ats_friendly": match_ratio >= 50
    }

# Run the script
if __name__ == "__main__":
    file_path = sys.argv[1]  # CV File Path
    job_description = sys.argv[2]  # Job Description
    result = is_ats_friendly(file_path, job_description)
    print(result)
