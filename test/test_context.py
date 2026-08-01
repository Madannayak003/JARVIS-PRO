from ai.conversation import *

set_context("last_app", "chrome")
set_context("last_song", "Believer")

print(get_context("last_app"))
print(get_context("last_song"))

print(all_context())