import json
from typing import List

from ollama import ChatResponse
from ollama import chat as ollama_chat
from pydantic import BaseModel

from config import DATA_PATH

# load computrabajo files
file = DATA_PATH / "compu_trabajo_job_offers_20260120_23_00.json"

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)


class ExperienceSchema(BaseModel):
    minimum_years: int
    areas: List[str]


class TechnologiesSchema(BaseModel):
    cloud: List[str] | None
    frameworks: List[str] | None
    languages: List[str] | None
    databases: List[str] | None
    big_data: List[str] | None
    architectures: List[str] | None
    others: List[str] | None


class WorkModeSchema(BaseModel):
    type: str
    on_site_days_per_week: int
    location: str
    salary: float | None


class JobOfferSchema(BaseModel):
    position: str
    work_mode: WorkModeSchema
    job_type: List[str]
    technologies: TechnologiesSchema
    experience_required: ExperienceSchema
    skills: List[str]


def parse_llm_response_to_json(response_content: str) -> dict:
    """Parse the LLM response content to a JSON dictionary."""
    try:
        # Clean the response content
        cleaned_content = response_content.replace("```json\n", "").rstrip("```\n")
        # Parse the cleaned content to a JSON object
        json_data = json.loads(cleaned_content)
        return json_data
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return {}


def job_template(description: str, requirements: str) -> str:
    schema = JobOfferSchema.model_json_schema()

    return f"""
    Con la descripcion y los requerimientos, resume la siguiente oferta laboral, ignora en nombre de la empresa, mision, vison etc. 
    lo que importa es Tecnologías necesarias, tipo de trabajo (remoto, presencial etc). Retorna la informacion en formato JSON (string)
    con la siguiente estructura:
    
    ```json
    {schema}
    ```

    <description>
        {description}
    </description>

    <requirements>
        {requirements}
    </requirements>
    """


for job in data:
    description = job["details"]["description"]
    requirements = job["details"]["requirements"]
    job_prompt = job_template(description, requirements)

    response: ChatResponse = ollama_chat(
        model="gemma3",
        messages=[
            {
                "role": "user",
                "content": job_prompt,
            },
        ],
    )
    print(response["message"]["content"])
    # or access fields directly from the response object
    job["llm_parsed"] = parse_llm_response_to_json(response.message.content)
