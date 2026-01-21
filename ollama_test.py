import json
from typing import List

from ollama import ChatResponse, chat
from pydantic import BaseModel


class ExperienceSchema(BaseModel):
    minimum_years: int
    areas: List[str]


class TechnologiesSchema(BaseModel):
    cloud: List[str]
    languages: List[str]
    databases: List[str]
    big_data: List[str]
    architectures: List[str]
    others: List[str]


class WorkModeSchema(BaseModel):
    type: str
    on_site_days_per_week: int
    location: str


class JobOfferSchema(BaseModel):
    position: str
    work_mode: WorkModeSchema
    job_type: List[str]
    technologies: TechnologiesSchema
    experience_required: ExperienceSchema
    skills: List[str]


def job_template(description: str) -> str:
    schema = JobOfferSchema.model_json_schema()

    return f"""
    Resume la siguiente oferta laboral, ignora en nombre de la empresa, mision, vison etc. 
    lo que importa es Tecnologías necesarias, tipo de trabajo (remoto, presencial etc). Retorna la informacion en formato JSON (string)
    con la siguiente estructura:
    
    ```json
    {schema}
    ```

    NOTA: No agregues "```json" ni "```" al inicio o final de la respuesta, solo el JSON puro.

    <description>
        {description}
    </description>
    """


description = """
AIT es una empresa mexicana con 15 años de experiencia en reclutamiento y administración 
de profesionales en tecnologías de la información, nuestra esencia es la atracción y 
gestión de talento para áreas de sistemas. Buscamos personas apasionadas y comprometidas 
para brindarles la mejor experiencia. Tú elijes tu camino profesional y nosotros te 
acompañamos durante cada etapa para crear una trayectoria profesional que sea única. 
Arquitecto de Datos Para liderar el diseño y la evolución de nuestras plataformas de datos. 
La persona ideal tendrá una sólida experiencia construyendo soluciones escalables en la nube, 
modelos de datos avanzados y arquitecturas modernas orientadas a analítica y procesamiento 
de grandes volúmenes de información. Responsabilidades Diseñar la arquitectura 
de datos empresarial (modelos, estándares, integraciones). Liderar iniciativas 
de Data Lake, Data Warehouse o Lakehouse. Definir mejores prácticas de gobierno, 
calidad y seguridad de datos. Colaborar con equipos de ingeniería y negocio para 
transformar necesidades en soluciones. Evaluar y optimizar pipelines, bases de datos 
y sistemas de procesamiento. Implementar tecnologías de integración y procesamiento 
en tiempo real (streaming). Requisitos +5 años en ingeniería/arquitectura de datos o similares. 
Experiencia con nubes (AWS, Azure o GCP). Dominio de SQL y al menos un lenguaje como Python o Scala. 
Conocimientos en bases de datos SQL/NoSQL y herramientas Big Data (Spark, Kafka, etc.).
Experiencia con arquitecturas modernas: Lakehouse, Data Mesh o Event-Driven. 
Habilidades Blandas Comunicación clara y capacidad de influenciar decisiones técnicas. 
Pensamiento estratégico y enfoque en escalabilidad. Trabajo colaborativo con equipos 
multidisciplinarios. Ofrecemos Proyectos de alto impacto. Ambiente ágil y de innovación Modalidad hibrida 
(3 veces a la semana presencial) Zona: Montes Urales. ¡Únete al mejor equipo del trabajo! 
Envíanos tu información en el correo mencionado o postúlate por este medio. 
Dentro de los procesos de Reclutamiento y Selección de personal en AIT, 
se respeta plenamente la dignidad humana del trabajador; no existe discriminación por 
origen étnico o nacional, género, edad, discapacidad, condición social, condiciones de salud, 
religión, condición migratoria, opiniones, preferencias sexuales o estado civil; se tiene acceso a 
la seguridad social y se percibe un salario remunerador; 
se recibe capacitación continua para el incremento de la productividad con beneficios.
"""

job_prompt = job_template(description)

response: ChatResponse = chat(
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
print(response.message.content)

json.loads(response.message.content.replace("```json\n", "").rstrip("```\n"))
