# import core.__init__
from skills.loader import load_all
from core.assistant import run
from ai.memory import init_memory
from core.services import start_all

if __name__ == "__main__":
    
    load_all()
    
    init_memory()
    
    start_all()
    
    run()