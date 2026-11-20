"""Entity/relationship extraction for Article B8 (Car & Component Limitations). Writes data/extractions/B8.json."""

from common import *
PU, HD, C4 = "power unit", "pu homologation dossier", "appendix c4"
ELEMS = {"internal combustion engine": "max 3 per driver per Championship",
         "turbocharger": "max 3 per driver per Championship",
         "exhaust set": "max 3 per driver per Championship; its four parts are counted separately",
         "energy store": "max 2 per driver per Championship",
         "power unit control electronics": "max 2 per driver per Championship",
         "mgu-k": "max 2 per driver per Championship",
         "power unit ancillary component": "max 5 of each per driver per Championship"}
MENTIONS = {
"B8.1.1": ["competitor", "f1 car", "competition", "survival cell", "technical delegate", "fia"],
"B8.1.2": ["f1 car", "survival cell", PU, "technical regulations", C4],
"B8.2.1": [PU, "competition", "championship", HD, "fia seal"],
"B8.2.2": ["championship", "driver", "competitor", C4, PU] + list(ELEMS),
"B8.2.3": ["driver", PU, "championship", "power unit manufacturer"],
"B8.2.4": ["power unit ancillary component", "driver", HD, "fia", "fia seal"],
"B8.2.5": ["fia", "sspuc component", PU],
"B8.2.6": ["fia", "sspuc component", "championship", "sspuc supplier", "power unit manufacturer"],
"B8.2.7": ["driver", "championship", "replacement driver", PU],
"B8.2.8": ["driver", PU, "championship", "grid place penalty", "competition", "race", "f1 car", "transponder", "pit lane", "power unit allocation exceeded"],
"B8.2.9": ["power unit manufacturer", "fia", "fia seal", PU, "competition", "energy store", "power unit control electronics", C4,
           "internal combustion engine", "turbocharger", "mgu-k", "parc fermé", "technical delegate", "fp1", "competitor", "designated garage area",
           "f1 car", "championship"],
"B8.2.10": [C4, PU, "fia seal", "fia", HD],
"B8.2.11": ["minor part", C4, "fia", HD, "fia seal"],
}
add_fact("B8.1.1", "competitor", "REQUIRES", "f1 car", context="max two cars available at any time, except while changing a survival cell")
add_fact("B8.1.1", "technical delegate", "CONTROLS", "survival cell", context="approves a change after genuine accident damage or a significant failure, on written request")
add_fact("B8.1.2", "f1 car", "HAS_PART", "survival cell", PU, context="for B8.1 a car is a survival cell with a power unit (or parts of one) installed")
add_fact("B8.1.2", PU, "DEFINED_IN", "technical regulations", context="Article C1 (Part B)")
add_fact("B8.1.2", PU, "DEFINED_IN", C4)
add_fact("B8.2.1", PU, "DEFINED_IN", HD, context="elements must conform to the latest approved homologation dossier when entered into the pool")
add_fact("B8.2.1", PU, "REQUIRES", "fia seal", context="only sealed elements may be used during a Competition")
for e, c in ELEMS.items():
    add_fact("B8.2.2", PU, "HAS_PART", e, context=c)
    add_fact("B8.2.2", e, "DEFINED_IN", C4)
add_fact("B8.2.3", "power unit manufacturer", "ALLOCATES", PU, context="one extra unit of each element per driver in 2026, or with a PU Manufacturer in its first year of supply")
add_fact("B8.2.4", "power unit ancillary component", "DEFINED_IN", HD, context="sealing or identification method approved by the FIA; may move between a driver's sealed elements without penalty")
add_fact("B8.2.5", "fia", "CONTROLS", "sspuc component", context="may authorise or mandate replacement for safety, policing or reliability")
add_fact("B8.2.6", "fia", "CONTROLS", "sspuc component", context="may raise the number permitted for a genuine reliability issue after consulting the SSPUC supplier and PU manufacturers")
add_fact("B8.2.7", "replacement driver", "REQUIRES", PU, context="counted as the original driver for power unit usage")
add_fact("B8.2.8", "power unit allocation exceeded", "PUNISHABLE_BY", "grid place penalty", context="first extra element of each type: 10 places; each later one: 5 places; cumulative; applied at the Competition where it is first used")
add_fact("B8.2.8", "grid place penalty", "APPLIES_DURING", "race", context="power unit element penalties")
add_fact("B8.2.8", "transponder", "DETERMINES", "power unit allocation exceeded", context="an element counts as used once the transponder shows the car left the pit lane")
add_fact("B8.2.9", "fia", "CONTROLS", "fia seal", context="seals each PU element before its first use, after consulting the PU manufacturer; ESME sealed to protect ES and PU-CE parts")
add_fact("B8.2.9", "technical delegate", "CONTROLS", "fia seal", context="agrees the sealing method; extra ICE/TC/MGU-K seals applied within 2 h of post-Race parc fermé, removed 50 h before FP1 on request")
add_fact("B8.2.9", PU, "OCCURS_AT", "designated garage area", context="elements stay there when not fitted; no cranking or starting until 26 h before FP1")
add_fact("B8.2.9", PU, "REQUIRES", "fia seal", context="parts with damaged or removed seals may not be reused unless removed under FIA supervision")
add_fact("B8.2.10", PU, "DEFINED_IN", C4, context="parts listed EXC in column 5 may be changed without a B8.2.8 penalty; breaking a seal requires FIA supervision")
add_fact("B8.2.10", PU, "DEFINED_IN", HD, context="changed EXC parts must be homologated per Appendix C5")
add_fact("B8.2.11", "minor part", "DEFINED_IN", C4)
add_fact("B8.2.11", "minor part", "DEFINED_IN", HD, context="approved by the FIA; may be changed without penalty but without breaking a seal")
build("B8", MENTIONS)
