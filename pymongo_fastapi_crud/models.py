from typing import Union
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class UnlabeledJob(BaseModel):
    company: Union[str, None] = None
    job_id: Union[str, None] = None
    placement_term: Union[str, None] = None
    job_title_: Union[str, None] = None
    position_type: Union[str, None] = None
    job_location: Union[str, None] = None
    country: Union[str, None] = None
    duration: Union[str, None] = None
    salary_currency: Union[str, None] = None
    salary: Union[str, None] = None
    job_description: Union[str, None] = None
    job_requirements: Union[str, None] = None
    citizenship_requirement: Union[str, None] = None
    application_deadline: Union[str, None] = None
    application_procedure: Union[str, None] = None
    address_cover_letter_to: Union[str, None] = None
    application_documents_required: Union[str, None] = None
    special_application_instructions: Union[str, None] = None
    important_urls: Union[str, None] = None
    probability: Union[float, None] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "company": "TC Energy",
                "job_id": "164100",
                "placement_term": "2025 - Summer",
                "job_title_": "S25 Indigenous Relations Intern 164100",
                "position_type": "Co-op Position",
                "job_location": "Calgary, AB",
                "country": "Canada",
                "duration": "4 months",
                "salary_currency": "CAD",
                "salary": "Salary Not Available, 0 hours per week",
                "job_description": "Job Title: May 2025 Indigenous Relations Intern\n\nJob ID: JR-07052\n\nApplication Deadline: December 13, 2024\n\nDetermined. Imaginative. Curious. If these are some of the ways you describe yourself - we want to learn more about you! At TC Energy, we are Energy Problem Solvers - passionate about transitioning North America to cleaner energy while meeting the energy demands of today and tomorrow. If that sounds like a challenge you want to help tackle, we want you to join our team!\n\nThe Opportunity\n\nTC Energy is looking to add an #EnergyProblemSolver in Calgary to support our efforts in Energy Problem Solving and our daily operations.\n\nWe are seeking a student enrolled in Bachelor of Commerce, Bachelor of Business Administration or related Programs, in various majors and specializations.\n\nWe engage our BComm/BBA students in the very core of our operations. As a valued member of the team, you'll do exciting, challenging work, solve real world problems, and make a meaningful impact. You'll learn about the business and build your professional network by working closely with other skilled people at TC Energy. Every day will enhance your knowledge, skills and passion for what you do.\n\nThe term length is 4 months.\n\nRole is based in Calgary, AB.\n\nWhat you'll do\n\nAssist with organizing community meetings and events\nAssist with internal Governance of Indigenous Relations function\nAttend site visits and provide support in maintaining community investment programming\nSupport Indigenous Relations engagement team members\nMaintain and update databases to ensure the evidentiary record of engagement with Indigenous groups, representatives and members, is maintained and accurate, to support regulatory filings and ongoing relationship building\nProvide administrative support to achieve department goals and execute projects",
                "job_requirements": "Minimum Qualifications\n\nActively enrolled in a BComm / BBA undergraduate degree program, communications or equivalent, with at least one semester of education complete\nEnrollment at an accredited university, and returning to school for at least one semester following your work term\nExhibit a safety mindset, in a professional and personal setting\nMust exhibit the TC Energy corporate values and incorporate them into work activities and initiatives: safety, responsibility, integrity, innovation and collaboration\n\nPreferred Qualifications\n\nStrong interpersonal and communicative skills to work efficiently in a collaborative team environment\nCommitted to building and maintaining relationships with internal and external stakeholders\nAbility to accurately analyze information and deal with ambiguity\nExperience working in a dynamic and challenging environment, and adaptable to changing priorities\nAbility to multi-task effectively, with strong organizational and time management skills\nReflective and committed to continuous improvement and personal development\n\nTo remain competitive, support our high-performance culture and allow for more flexibility in the way we work, we offer a hybrid work model and flexible dress code for our eligible office-based workforce in Canada, the U.S. and Mexico. #LI-Hybrid",
                "citizenship_requirement": "N/A",
                "targeted_co-op_programs": "View Targeted Programs",
                "application_deadline": "December 13, 2024 11:59 PM",
                "application_procedure": "Through Employer Website",
                "cover_letter_required?": "Yes",
                "address_cover_letter_to": "Hiring Manager",
                "application_documents_required": "Job Application Summary Sheet,Cover Letter,Resume on Co-op Footer,UBC Transcript",
                "special_application_instructions": "Application Link:\n\nhttps://tcenergy.wd3.myworkdayjobs.com/en-US/CAREER_SITE_TC/job/May-2025-Indigenous-Relations-Intern_JR-07052\n\nPlease apply with a Resume, Cover Letter and Transcript.\n\nApplication Deadline: December 13, 2024",
                "important_urls": "https://tcenergy.wd3.myworkdayjobs.com/en-US/CAREER_SITE_TC/job/May-2025-Indigenous-Relations-Intern_JR-07052",
                "probability": 80
            }
        }


class ProbabilityUpdate(BaseModel):
    job_id: str
    probability: float

    class Config:
        json_schema_extra = {
            "example": [
                {"job_id": "job123", "probability": 0.85},
                {"job_id": "job456", "probability": 0.75},
                {"job_id": "job789", "probability": 0.95}
            ]
        }


class LabelledJob(BaseModel):
    company: Union[str, None] = None
    job_id: Union[str, None] = None
    placement_term: Union[str, None] = None
    job_title_: Union[str, None] = None
    position_type: Union[str, None] = None
    job_location: Union[str, None] = None
    country: Union[str, None] = None
    duration: Union[str, None] = None
    salary_currency: Union[str, None] = None
    salary: Union[str, None] = None
    job_description: Union[str, None] = None
    job_requirements: Union[str, None] = None
    citizenship_requirement: Union[str, None] = None
    application_deadline: Union[str, None] = None
    application_procedure: Union[str, None] = None
    address_cover_letter_to: Union[str, None] = None
    application_documents_required: Union[str, None] = None
    special_application_instructions: Union[str, None] = None
    important_urls: Union[str, None] = None
    apply: Union[int, None] = None
