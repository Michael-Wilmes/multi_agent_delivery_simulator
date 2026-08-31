from pathlib import Path
from app.config import load_config
from app.simulation.engine import SimulationEngine
from app.ui.app import SimulatorApp

def main():
    root=Path(__file__).resolve().parent
    config=load_config(root/'config'/'app.json')
    SimulatorApp(SimulationEngine(config),config).run()

if __name__=='__main__': main()
