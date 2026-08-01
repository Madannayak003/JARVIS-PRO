from ai.planner import create_plan
from core.executor import execute_ai_plan

plan = create_plan(

    "Open Chrome and search YouTube for ESP32 tutorial"

)

execute_ai_plan(plan)