from brain.developer.developer_context import DeveloperContext

ctx = DeveloperContext()

print(ctx.has_pending())

ctx.save("Write calculator code")

print(ctx.has_pending())

print(ctx.merge("Python"))

print(ctx.has_pending())