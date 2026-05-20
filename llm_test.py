import json
import os
from typing import List, Literal

from openai import OpenAI
from pydantic import BaseModel

from dotenv import load_dotenv

from config import DATA_PATH, Config

load_dotenv()

client = OpenAI(
    api_key=Config.DEEP_SEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

# load computrabajo files
file = DATA_PATH / "occ_job_offers_20260501_09_00.json"

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)


class ExperienceSchema(BaseModel):
    minimum_years: int
    areas: List[str]


class SalarySchema(BaseModel):
    amount: float | None
    currency: Literal["USD", "EUR", "GBP", "JPY", "CNY", "INR", "MXN", "BRL", "ARS"] = (
        "MXN"
    )
    period: Literal["monthly", "yearly", "weekly", "daily", "hourly"] | None


class ProgrammingLanguageSchema(BaseModel):
    name: str | None = None
    level: Literal["beginner", "intermediate", "advanced", "expert"] | None = None
    libraries: List[str] | None = None


class TechnologiesSchema(BaseModel):
    cloud: List[str] | None
    frameworks: List[str] | None
    programming_languages: List[ProgrammingLanguageSchema] | None
    databases: List[str] | None
    big_data: List[str] | None
    architectures: List[str] | None
    others: List[str] | None


class WorkModeSchema(BaseModel):
    mode: Literal["remote", "onsite", "hybrid"] | None
    on_site_days_per_week: int | None
    location: str | None
    salary: SalarySchema | None


class LanguageSchema(BaseModel):
    name: (
        Literal["English", "Spanish", "French", "German", "Chinese", "Japanese"] | None
    ) = None
    language_proficiency_level: (
        Literal["native", "A1", "A2", "B1", "B2", "C1", "C2"] | None
    ) = None


class JobOfferSchema(BaseModel):
    position: str
    work_mode: WorkModeSchema
    job_type: List[str]
    technologies: TechnologiesSchema
    experience_required: ExperienceSchema
    skills: List[str]
    foreign_languages: List[LanguageSchema]


def parse_llm_response_to_json(response_content: str) -> JobOfferSchema | dict:
    """Parse the LLM response content to a JSON dictionary."""
    try:
        # Clean the response content
        cleaned_content = response_content.replace("```json\n", "").rstrip("```\n")
        # Parse the cleaned content to a JSON object
        json_data = json.loads(cleaned_content)
        return JobOfferSchema.model_validate(json_data)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return {}


class DetailsSchema(BaseModel):
    description: str | None = None
    requirements: str | None = None
    salary: str | None = None
    time: str | None = None


class ScrapedJobOfferSchema(BaseModel):
    title: str
    company: str
    location: str
    relative_date: str
    details: DetailsSchema


def job_template(job: ScrapedJobOfferSchema) -> str:
    schema = JobOfferSchema.model_json_schema()

    return f"""
        ### Role
        Act as a precise IT Recruitment Data Analyst. Your goal is to parse job descriptions into a structured JSON that adheres strictly to a provided Pydantic schema.

        ### Strict Constraints
        1. **Output Format:** Return ONLY the raw JSON string. No markdown blocks, no "Here is your JSON", no explanations.
        2. **Language:** Translate all extracted text values to **English**, except for proper technology names.
        3. **Data Integrity:**
            - **Enums:** You MUST use only the values defined in the schema (e.g., `WorkMode` must be exactly "remote", "onsite", or "hybrid").
            - **Currency:** Default to "MXN" unless specified. Use only valid codes: [USD, EUR, GBP, JPY, CNY, INR, MXN, BRL, ARS].
            - **Proficiency:** Use only [native, A1, A2, B1, B2, C1, C2].
        4. **Noise Filtering:** Ignore company history, perks (coffee, gym), and non-technical marketing text.

        ### Inference & Nulls
        - If a field is missing (e.g., salary amount), attempt to infer it from context.
        - If inferred, add a clear note in the `others` array under `technologies` or a relevant `skills` entry stating: "[Inferred]: field_name".
        - If a field is not present and cannot be inferred, set it to `null`.
        - For `on_site_days_per_week`, if the mode is "remote", set to 0. If "onsite", set to 5.

        ### Input Data
        - **Description:** {job.details.description}
        - **Requirements:** {job.details.requirements}
        - **Metadata:** {job.details.salary}

        ### Target Schema (JSON Schema)
        {schema}
    """


# Create and empty file and write each resulting JSON on a new line

for job in data:
    current_job = ScrapedJobOfferSchema.model_validate(job)
    job_prompt = job_template(current_job)

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": job_prompt,
            },
        ],
    )
    parsed_data = parse_llm_response_to_json(response.choices[0].message.content)
    final_data = (
        parsed_data.model_dump_json(exclude_none=True)
        if isinstance(parsed_data, JobOfferSchema)
        else {}
    )
    print("\n" + final_data)

    with open("occ_job_offers_llm_parsed.jsonl", "a", encoding="utf-8") as f:
        f.write(final_data + "\n")

    job["llm_parsed"] = final_data
