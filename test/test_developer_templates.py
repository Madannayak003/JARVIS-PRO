from brain.developer.developer_detector import DeveloperDetector
from brain.developer.developer_defaults import DeveloperDefaultsEngine
from brain.developer.developer_templates import DeveloperTemplateBuilder

detector = DeveloperDetector()

defaults = DeveloperDefaultsEngine()

builder = DeveloperTemplateBuilder()

request = detector.detect(
    "Write Python calculator"
)

default_data = defaults.build(request)

prompt = builder.build(
    request,
    default_data
)

print(prompt)