import os 
from dotenv import load_dotenv 
from google import genai 

load_dotenv()

key = os.getenv("GEMINI_API_KEY", "")
model = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"

def extract_repair_tasks(report: str) -> list[str] :
    client = genai.Client(api_key= key)
    prompt = "\n".join(
        [
            "Find out every repair or follow up job arising from the inpection report given.",
            "Require the reply to carry one job per line.",
            "Each line opening with the marker 'REPAIR:' followed by the job.",
            "Do not invent jobs, and preserve named location, deadline, and urgency.",
            f"Report: {report}"
        ]
    )
    response = client.models.generate_content(model= model, contents= prompt)
    if response.text is None :
        raise ValueError()
    return [
        line.strip().removeprefix("REPAIR:").strip()
        for line in response.text.splitlines()
        if line.strip().startswith("REPAIR:")
    ]

def assign_technician_and_urgency(task: str, crew: list[str]) -> tuple[str, str] :
    client = genai.Client(api_key= key)
    prompt= "\n".join(
        [
            "Select exactly one technician from the crew list supplied and copy the name as written for the given task.",
            "Require the urgency to be one of 'High', 'Medium' or 'Low' strictly.",
            "Require the reply as exactly two lines.",
            "First Line -> 'TECHNICIAN:' <crew member>",
            "Second Line -> 'URGENCY:' <'High', 'Medium' or 'Low'>",
            f"Task: {task}",
            f"crew: {"\n".join(crew)}"
        ]
    )
    response = client.models.generate_content(model= model, contents= prompt)
    if response.text is None :
        raise ValueError()
    fields = {}
    for line in response.text.splitlines() :
        label, value = line.strip().split(":")
        if label.strip() in {"TECHNICIAN", "URGENCY"} :
            fields[label.strip()] = value.strip()
    if "TECHNICIAN" not in fields or "URGENCY" not in fields :
        raise ValueError()
    technician = fields["TECHNICIAN"]
    urgency = fields["URGENCY"]
    if technician not in crew or urgency not in {'High', 'Medium', 'Low'} :
        raise ValueError()
    return technician, urgency