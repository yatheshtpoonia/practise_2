import json 
from langchain_core.messages import AIMessage
from state import InspectionState
from agents import extract_repair_tasks, assign_technician_and_urgency

path = "data/inspection_reports.json"

def load_inspection(state: InspectionState) -> dict :
    inspection_id = input().strip()
    with open(path) as f :
        inspections = json.load(f)["inspections"]
    for inspection in inspections :
        if inspection["inspection_id"] == inspection_id :
            return {
                "messages": [AIMessage(content= f"{inspection_id}")],
                "inspection_id": inspection_id, 
                "property": inspection["property"],
                "crew": inspection["crew"],
                "report": inspection["report"],
                "status" : "extracting"
            }
    return {
        "messages": [AIMessage(content= f"{inspection_id}")],
        "inspection_id": inspection_id, 
        "property": "",
        "crew": [],
        "report": "",
        "status" : "completed"
    }

def extract_repairs(state: InspectionState) -> dict :
    if not state["report"] :
        return {
            "messages" : [AIMessage(content= "Report not found")],
            "work_orders" : [],
            "status" : "completed"
        }
    tasks = extract_repair_tasks(state["report"])
    return {
        "messages" : [AIMessage(content= f"{len(tasks)}")],
        "work_orders" : [{"task" : task, "technician" : "", "urgency" : ""} for task in tasks],
        "status" : "assigning"
    }

def assign_technicians(state: InspectionState) -> dict :
    orders = []
    for order in state["work_orders"] :
        technician, urgency = assign_technician_and_urgency(order["task"], state["crew"])
        orders.append({"task" : order["task"], "technician" : technician, "urgency" : urgency})
    return {
        "work_orders" : orders,
        "messages" : [AIMessage(content= f"{len(orders)}")]
    }

def format_summary(state: InspectionState) -> dict :
    lines = [
        "Summary",
        f"Inspection ID : {state['inspection_id']}",
        f"Property: {state['property']}",
        f"Crew: {','.join(state['crew'])}",
        f"Work Orders: {len(state['work_orders'])}",
    ]
    for index, order in enumerate(state["work_orders"], start= 1) :
        lines.append(f"{index}. [{order['urgency']}] {order['task']}")
        lines.append(f"Technician: {order['technician']}")
    return {
        "messages" : [AIMessage(content= f"{len(lines)}")],
        "summary" : "\n".join(lines),
        "status" : "completed"
    }