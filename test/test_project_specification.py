from brain.developer.project_specification import ProjectSpecificationBuilder

builder = ProjectSpecificationBuilder()

tests = [

    ("arduino", "LED_Blink"),

    ("esp32", "WiFi_LED"),

    ("python", "Calculator"),

    ("html", "Login_Page")

]

for language, project in tests:

    print("=" * 60)

    spec = builder.build(

        language,

        project

    )

    print(spec)