# MACROS for particle types in the simulation
GAS = 0
DARKMATTER = 1
STAR = 4
BLACKHOLE = 5

from typing import Literal
_SIM_NAME_HINTS = Literal["L200N64_DMO","L200N64_Hydro"]

from ninja.MPGadgetExtention import Simulation, _METALS
METALS = _METALS()

