import json
import os
from typing import List, Literal

from openai import OpenAI
from pydantic import BaseModel

from dotenv import load_dotenv

from config import DATA_PATH, Config, PROCESS_DATA_PATH

load_dotenv()

client = OpenAI(
    api_key=Config.DEEP_SEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

OFFER_WEB_NAME = "compu_trabajo"
FILE_NAME = f"{OFFER_WEB_NAME}_job_offers_20260523_10_00"

# load computrabajo files
file = DATA_PATH / f"{FILE_NAME}.json"

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)
    # limit to first 20 for testing
    data = data[:20]


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


def parse_llm_response_to_json(response_content: str) -> List[JobOfferSchema]:
    """Parse the LLM response (JSON array) into a list of JobOfferSchema."""
    try:
        cleaned_content = (
            response_content.strip().removeprefix("```json").removesuffix("```").strip()
        )
        json_data = json.loads(cleaned_content)
        return [JobOfferSchema.model_validate(item) for item in json_data]
    except Exception as e:
        print("Error decoding JSON:", e)
        return []


class DetailsSchema(BaseModel):
    description: str | None = None
    requirements: str | None = None
    salary: str | None = None
    time: str | None = None
    place: str | None = None


class ScrapedJobOfferSchema(BaseModel):
    title: str
    company: str
    location: str
    relative_date: str
    details: DetailsSchema


BATCH_SIZE = 5


def jobs_template(jobs: List[ScrapedJobOfferSchema]) -> str:
    schema = JobOfferSchema.model_json_schema()

    jobs_input = "\n\n".join(
        f"### Job {i + 1}\n"
        f"- **Description:** {job.details.description}\n"
        f"- **Requirements:** {job.details.requirements}\n"
        f"- **Metadata:** Salary: {job.details.salary or "<Not specified>"},"
        f" time: {job.details.time or "<Not specified>"}, mode: {job.details.place or "<Not specified>"}\n"
        for i, job in enumerate(jobs)
    )

    return f"""
        ### Role
        Act as a precise IT Recruitment Data Analyst. Your goal is to parse job descriptions into structured JSON objects that adhere strictly to a provided Pydantic schema.

        ### Strict Constraints
        1. **Output Format:** Return ONLY a raw JSON array with exactly {len(jobs)} objects — one per job, in the same order. No markdown blocks, no explanations.
        2. **Language:** Translate all extracted text values to **English**, except for proper technology names.
        3. **Data Integrity:**
            - **Enums:** You MUST use only the values defined in the schema (e.g., `WorkMode` must be exactly "remote", "onsite", or "hybrid").
            - **Currency:** Default to "MXN" unless specified. Use only valid codes: [USD, EUR, GBP, JPY, CNY, INR, MXN, BRL, ARS].
            - **Proficiency:** Use only [native, A1, A2, B1, B2, C1, C2].
        4. **Noise Filtering:** Ignore company history, perks (coffee, gym), and non-technical marketing text.

        ### Inference & Nulls
        - If a field is missing, attempt to infer it from context.
        - If inferred, add a note in the `others` array under `technologies` stating: "[Inferred]: field_name".
        - If a field is not present and cannot be inferred, set it to `null`.
        - For `on_site_days_per_week`, if the mode is "remote", set to 0. If "onsite", set to 5.

        ### Input Jobs
        {jobs_input}

        ### Target Schema (apply to each object in the array)
        {schema}
    """


OUTPUT_FILE = PROCESS_DATA_PATH / f"{FILE_NAME}_llm_parsed.jsonl"

with open(OUTPUT_FILE, "a", encoding="utf-8") as out_file:
    for batch_start in range(0, len(data), BATCH_SIZE):
        batch = data[batch_start : batch_start + BATCH_SIZE]
        current_jobs = [ScrapedJobOfferSchema.model_validate(job) for job in batch]

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": jobs_template(current_jobs)}],
        )

        parsed_batch = parse_llm_response_to_json(response.choices[0].message.content)

        for i, parsed in enumerate(parsed_batch):
            final_data = parsed.model_dump_json(exclude_none=True)
            print("\n" + final_data)
            out_file.write(final_data + "\n")
            batch[i]["llm_parsed"] = final_data
