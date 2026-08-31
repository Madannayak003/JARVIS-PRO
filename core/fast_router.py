from core.routers.news_router import news_route

from core.routers.browser_router import browser_route
from core.routers.system_router import system_route
from core.routers.automation_router import automation_route
from core.routers.network_router import network_route
from core.routers.media_router import media_route
from core.routers.file_router import file_route
from core.routers.vision_router import vision_route
from core.routers.spotify_router import spotify_route
from core.routers.greeting_router import greeting_route
from core.routers.whatsapp_router import whatsapp_route
from core.routers.contact_router import contact_route
from core.routers.file_selection_router import file_selection_route
from core.routers.memory_router import memory_route
from core.routers.web_router import web_route

ROUTERS = [

    memory_route,
    
    news_route,
    
    web_route,
    
    automation_route,

    browser_route,
    
    spotify_route,
    
    greeting_route,

    system_route,

    network_route,

    media_route,

    file_route,
    
    vision_route,
    
    contact_route,
    
    whatsapp_route,
    
    file_selection_route

]

def fast_route(command):

    command = command.lower().strip()

    print("[FAST ROUTER]", command)

    for router in ROUTERS:

        plan = router(command)

        if plan:

            print("[FAST ROUTER MATCH]", plan)

            return plan

    return None

