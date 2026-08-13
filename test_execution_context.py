from brain.execution_context import (
    ExecutionContextResolver
)


resolver = ExecutionContextResolver()


print("\n[TEST 1] Spotify play")

result = resolver.resolve(
    "spotify_play"
)

print(result)


print("\n[TEST 2] Spotify pause")

result = resolver.resolve(
    "spotify_pause"
)

print(result)


print("\n[TEST 3] Spotify volume up")

result = resolver.resolve(
    "spotify_volume_up"
)

print(result)


print("\n[TEST 4] YouTube play")

result = resolver.resolve(
    "youtube_play_first"
)

print(result)


print("\n[TEST 5] System volume")

result = resolver.resolve(
    "volume"
)

print(result)