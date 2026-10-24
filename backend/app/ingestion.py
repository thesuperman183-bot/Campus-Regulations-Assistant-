import io
from typing import List, Dict, Union, BinaryIO
from pypdf import PdfReader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

# Comprehensive SSIT Campus Regulations & Course Policy Pages
SAMPLE_PAGES = [
    """SSIT Academic Regulations & Course Guidelines (CS 101: Introduction to Programming).
    Instructor: Dr. A. Rao. Email: arao@ssit.edu. Office: Academic Block 2, Room A-312.
    Lectures are held Monday and Wednesday, 10:00 AM to 11:30 AM in Room B-204.
    Lab sessions are conducted on Friday from 2:00 PM to 4:00 PM in Computer Lab 3 (Room C-110).
    Office hours: Tuesday and Thursday 3:00 PM to 5:00 PM, or by appointment via college portal.
    This course provides foundational programming using Python for engineering undergraduates.
    Prerequisites: None. Open to all first-year engineering students.""",

    """Grading Breakdown and Assessment Policies.
    Continuous Internal Evaluation (CIE) comprises:
    1. Weekly lab programming assignments: 20%
    2. Two collaborative mini-projects: 30% (15% each)
    3. Midterm examination: 20%
    4. Semester End Examination (SEE) / Final Exam: 25%
    5. Classroom attendance and technical participation: 5%
    Grading Scale: 90% or above = Grade S/A+, 80% to 89% = Grade A, 70% to 79% = Grade B, 60% to 69% = Grade C, 50% to 59% = Grade D. Below 50% is failing (Grade F).
    Late Submission Policy: Late assignments lose 10% penalty per day up to a maximum of 3 days. After 3 days, late submissions receive zero credit.
    Grace Days: Every enrolled student receives two grace days per semester that can be used on lab assignments without penalty.""",

    """Curriculum Schedule and Examination Timetable.
    Weeks 1-2: Computational thinking, variables, data types, and I/O.
    Weeks 3-4: Control flow, conditional branching, iteration, and loops.
    Week 5: Functional abstraction, parameters, scope, and recursion.
    Week 6: Complex data structures (lists, tuples, dictionaries, and sets).
    Week 7: Midterm Examination (conducted in-class, closed book, 90 minutes).
    Weeks 8-9: File systems, persistent storage, and exception handling.
    Weeks 10-11: Web APIs, JSON processing, and data manipulation.
    Weeks 12-13: Mini-project Phase 2 demonstrations (teams of up to 3 students).
    Week 14: Comprehensive semester review and problem-solving workshops.
    Final Examination: 2-hour written and practical examination during the designated examination week.""",

    """Campus Academic Integrity, Attendance, and Device Policies.
    Attendance Requirement: Students must maintain a minimum of 75% attendance in both lectures and practical labs to be eligible for the Semester End Examination. Students with attendance between 65% and 74% due to medical reasons must submit a valid medical certificate within 3 days of return to the Head of Department. Students below 65% are detained.
    Academic Integrity & Plagiarism: All code submissions must represent original work. Peer collaboration for conceptual understanding is encouraged, but code copying is strictly forbidden.
    Generative AI Policy: AI tools (like ChatGPT or GitHub Copilot) may be utilized for debugging and learning assistance, provided their use is clearly declared in a comment header in the submission file. Submitting AI-generated code as uncredited original work is treated as academic malpractice.
    Lab Devices: Students are expected to bring their laptops with Python 3 installed. Students without laptops may reserve a workstation in the campus computer center.""",

    """SSIT Disciplinary Code, Grievances, and Extracurricular Exemptions.
    Campus Dress Code: Professional casual attire is expected during regular academic hours. Lab coats and closed footwear are mandatory in laboratory environments.
    Student Identity: Campus ID cards must be worn visibly at all times within the campus premises. ID cards are mandatory for library access, canteen billing, and entry into examination halls.
    Duty Leaves (On-Duty / OD): Students representing SSIT in recognized sports tournaments, technical hackathons, or cultural conferences may apply for up to 10 days of authorized Duty Leave per semester, which will be counted towards attendance.
    Grievance Redressal: Any academic evaluation dispute must be appealed in writing to the Controller of Examinations within 7 working days from the date of score announcement."""
]


def read_pdf(source: Union[str, bytes, BinaryIO]) -> List[str]:
    """
    Extracts text from each page of a PDF file.
    Accepts a filepath, raw bytes, or a file-like stream.
    Returns a list of page text strings.
    """
    if isinstance(source, bytes):
        stream = io.BytesIO(source)
        reader = PdfReader(stream)
    elif isinstance(source, str):
        reader = PdfReader(source)
    else:
        reader = PdfReader(source)

    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return pages


def split_into_chunks(pages: List[str], document_name: str) -> List[Dict]:
    """
    STAGE 1: Splits each page into overlapping chunks of about CHUNK_SIZE words.
    Preserves document name and original 1-based page number in each chunk dictionary.
    """
    chunks = []
    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)

    for page_number, text in enumerate(pages, start=1):
        words = text.split()
        for start in range(0, len(words), step):
            chunk_words = words[start:start + CHUNK_SIZE]
            if len(chunk_words) > 5:  # skip tiny fragments
                chunks.append({
                    "document": document_name,
                    "page": page_number,
                    "text": " ".join(chunk_words)
                })
            if start + CHUNK_SIZE >= len(words):
                break

    return chunks
