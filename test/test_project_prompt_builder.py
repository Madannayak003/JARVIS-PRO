from brain.developer.project.project_specification import ProjectSpecificationBuilder
from archive.project_planner_legacy import ProjectPlanner
from brain.developer.planner.project_prompt_builder import ProjectPromptBuilder

spec = ProjectSpecificationBuilder().build(
    "arduino",
    "RFID_Door_Lock"
)

plan = ProjectPlanner().build(spec)

prompt = ProjectPromptBuilder().build(

    spec,

    plan,

    "Create Arduino RFID Door Lock using MFRC522, Servo Motor, LCD and buzzer."

)

print(prompt)