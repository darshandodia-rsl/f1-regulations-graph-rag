"""Entity/relationship extraction for Article B3 (Procedures During A Competition). Writes data/extractions/B3.json."""

from common import *
MENTIONS = {
"B3.1.1": ["competitor", "scrutineering", "f1 car", "fp1", "technical delegate", "scrutineering declaration", "fia"],
"B3.1.2": ["f1 car", "competition", "scrutineering declaration", "technical delegate", "competitor"],
"B3.1.3": ["competitor", "f1 car", "survival cell", "scrutineering", "scrutineering declaration", "technical delegate", SFC, AFC, "fp1", "fp3", "pit lane exit", "race", "sprint"],
"B3.1.4": ["scrutineer", "f1 car", "competitor", "competition", "cover", "sprint qualifying", "qualifying", "sprint", "race", "formation lap", "fia", "fia seal", "technical delegate"],
"B3.1.5": ["race director", "f1 car"],
"B3.1.6": ["scrutineering", "official", "parc fermé", "competitor"],
"B3.1.7": ["competition", "competitor", "technical delegate", "scrutineering"],
"B3.1.8": ["steward", "scrutineer", "f1 car", "competition", REGS],
"B3.2.1": ["weighing", LT, "sprint qualifying", "qualifying", "f1 car", "driver", "fia garage", "internal combustion engine", "steward",
           "technical delegate", "pit lane", "fia scales", "designated garage area", "medical centre", "parc fermé", "q3", "sq3", "weighing breach"],
"B3.2.2": ["weighing", TT, "f1 car", "driver", "technical delegate"],
"B3.2.3": ["f1 car", "disqualification", "technical regulations", "weighing", "underweight car"],
"B3.2.4": ["f1 car", TT, "weighing", "scrutineer"],
"B3.2.5": ["weighing breach", "steward", "f1 car", "grid place penalty", "disqualification", "driver", TT],
"B3.3.1": ["covering of components", "fp1", "cover", "f1 car", "paddock", "designated garage area", "pit lane", "starting grid"],
"B3.3.2": ["covering of components", "cover", "internal combustion engine", "floor bodywork", "pit lane"],
"B3.3.3": ["cover", "f1 car", "rear wing bodywork", "internal combustion engine", "starting grid", "parc fermé", "pit lane", "tyre",
           "tyre supplier", "tyre blanket", "technical regulations"],
"B3.4.1": [SFC, "sealing of cars", "restricted period three", "competitor", "fp2", "f1 car", "pit lane", "fia seal", "cover", "floor bodywork",
           "nose bodywork", "front wing bodywork", "rear wing bodywork", "technical regulations", "parc fermé camera", "restricted period breach", "fp3"],
"B3.4.2": [AFC, "sealing of cars", "sprint qualifying", "f1 car", "pit lane", "fia seal", "technical delegate", "competitor",
           "parc fermé conditions", "driver", "penalty", "formation lap", "sprint", "cover"],
"B3.4.3": ["competition", "sealing of cars", "qualifying", "f1 car", "pit lane", "fia seal", "technical delegate", "competitor",
           "parc fermé conditions", "driver", "penalty", "formation lap", "race", "cover"],
"B3.4.4": ["f1 car", "cover", "fia seal"],
"B3.5.1": ["f1 car", "parc fermé conditions", "pit lane", "sprint qualifying", "sprint", "qualifying", "race", "sq1", "q1"],
"B3.5.2": ["competitor", "technical delegate", "suspension set-up sheet", "f1 car", "pit lane", "sprint qualifying", "qualifying"],
"B3.5.3": ["parc fermé conditions", "technical delegate", "f1 car", "sealing of cars", "parc fermé breach", SFC, AFC, "driver", "race",
           "sprint", "qualifying", "pit lane start"],
"B3.5.4": ["f1 car", "parc fermé conditions", "scrutineer", "pit lane", "technical delegate", "competitor", "fia", "sprint qualifying",
           "qualifying", "starting grid", "sprint", "reconnaissance lap", "race"],
"B3.5.5": ["championship", "front wing bodywork", "rear wing bodywork", "rear bodywork", "floor bodywork", "pre-season public collective testing",
           "sprint qualifying", "qualifying", TT, "parc fermé conditions"],
"B3.5.6": ["sprint qualifying", "qualifying", "fia", "f1 car", "competitor", "parc fermé"],
"B3.5.7": ["scrutineer", "f1 car", "parc fermé conditions", "front wing bodywork"],
"B3.5.8": ["scrutineer", "f1 car", "parc fermé conditions", "parc fermé camera", "competitor", "designated garage area", "competition", "fia-f1-doc-079"],
"B3.5.9": ["technical delegate", "f1 car", "parc fermé conditions", "competitor", "race"],
"B3.6.1": ["official", "parc fermé"],
"B3.6.2": ["parc fermé", "parc fermé conditions", "control line"],
"B3.6.3": ["parc fermé", "team personnel", "f1 car", "official"],
"B3.6.4": ["driver", "weighing", "helmet"],
"B3.6.5": ["driver", "parc fermé conditions"],
}
add_fact("B3.1.1", "competitor", "REQUIRES", "scrutineering", context="initial scrutineering starts 4 h before FP1")
add_fact("B3.1.1", "competitor", "REQUIRES", "scrutineering declaration", context="submitted no later than 2 h before FP1 unless the technical delegate allows otherwise; template provided by the FIA")
add_fact("B3.1.1", "scrutineering", "PRECEDES", "fp1")
add_fact("B3.1.2", "f1 car", "REQUIRES", "scrutineering declaration", context="may not take part until it is submitted and confirmed complete by the technical delegate")
add_fact("B3.1.2", "technical delegate", "CONTROLS", "scrutineering declaration", context="confirms it is fully and correctly completed")
add_fact("B3.1.3", "competitor", "REQUIRES", "scrutineering declaration", context="new declaration after a survival cell change")
add_fact("B3.1.3", "technical delegate", "CONTROLS", "scrutineering declaration", context="approves the new declaration after a survival cell change")
add_fact("B3.1.3", "f1 car", "HAS_PART", "survival cell")
add_fact("B3.1.4", "scrutineer", "CONTROLS", "f1 car", context="may check eligibility at any time, require dismantling, require parts or samples, and charge reasonable expenses")
add_fact("B3.1.4", "technical delegate", "CONTROLS", "fia seal", context="seals on shipped parts may only be broken with their written consent")
add_fact("B3.1.5", "race director", "CONTROLS", "f1 car", context="may require a car involved in an accident to be stopped and checked")
add_fact("B3.1.6", "official", "CONTROLS", "scrutineering", "parc fermé", context="duly appointed officials; only they may give instructions to Competitors")
add_fact("B3.1.7", "technical delegate", "CONTROLS", "scrutineering", context="from 24 h before the Competition, Competitors must supply team-specific tools and fixtures on request")
add_fact("B3.2.1", "weighing", "APPLIES_DURING", LT, "sprint qualifying", "qualifying")
add_fact("B3.2.1", "weighing", "APPLIES_DURING", "q3", "sq3", context="all cars that took part are weighed at the end")
add_fact("B3.2.1", "weighing", "OCCURS_AT", "fia garage", context="driver goes straight there when signalled and stops the engine")
add_fact("B3.2.1", "weighing", "OCCURS_AT", "fia scales", context="drivers weighed without undue delay after their last period or after stopping on track")
add_fact("B3.2.1", "technical delegate", "CONTROLS", "weighing", context="weighs each driver at the end of the last period they take part in")
add_fact("B3.2.1", "weighing breach", "APPLIES_DURING", "weighing", context="not stopping when signalled, or working on the car before it reaches the FIA garage: referred to the stewards")
add_fact("B3.2.2", "weighing", "APPLIES_DURING", TT, context="any classified car may be weighed")
add_fact("B3.2.3", "underweight car", "PUNISHABLE_BY", "disqualification", context="unless the shortfall is from accidental loss of a component")
add_fact("B3.2.3", "underweight car", "DEFINED_IN", "technical regulations", context="minimum weight in Article C4.1")
add_fact("B3.2.5", "weighing breach", "PUNISHABLE_BY", "grid place penalty")
add_fact("B3.2.5", "weighing breach", "PUNISHABLE_BY", "disqualification", context="from the TTCS")
add_fact("B3.2.5", "steward", "MAY_IMPOSE", "grid place penalty", "disqualification", context="weighing breach")
add_fact("B3.3.1", "covering of components", "OCCURS_AT", "paddock", "designated garage area", "pit lane", "starting grid",
  context="from 29 h before FP1 no cover may obscure any part of a car unless needed for mechanical reasons")
add_fact("B3.3.2", "covering of components", "REQUIRES", "cover", context="not permitted: engine/gearbox/radiator covers while engines are moved, covers over spare wings, spare floors or rigs used as screens")
add_fact("B3.3.3", "tyre blanket", "DEFINED_IN", "technical regulations", context="Article C10.8.4")
add_fact("B3.4.1", "sealing of cars", "APPLIES_DURING", SFC, context="cars covered and ready for FIA seals within 3 h of the end of FP2; seals removed 3 h before FP3")
add_fact("B3.4.1", "sealing of cars", "REQUIRES", "parc fermé camera", context="the complete car must stay in view of the camera")
add_fact("B3.4.1", "restricted period breach", "APPLIES_DURING", "sealing of cars", context="failing the FP2 sealing deadline counts as a Restricted Period 3 breach (single breach)")
add_fact("B3.4.1", "sealing of cars", "PRECEDES", "fp3")
add_fact("B3.4.2", "sealing of cars", "APPLIES_DURING", AFC, context="within 2 h of the end of Sprint Qualifying; seals removed 3 h before the Sprint formation lap, parc fermé conditions continue")
add_fact("B3.4.2", "technical delegate", "CONTROLS", "sealing of cars", context="may extend the deadline by up to 2 h for one car per Competitor for marketing")
add_fact("B3.4.3", "sealing of cars", "APPLIES_DURING", "competition", context="within 2 h of the end of Qualifying; seals removed 5 h before the Race formation lap, parc fermé conditions continue")
add_fact("B3.4.3", "technical delegate", "CONTROLS", "sealing of cars", context="may extend the deadline by up to 2 h for one car per Competitor for marketing")
add_fact("B3.5.1", "parc fermé conditions", "APPLIES_DURING", "sprint qualifying", context="from first leaving the pit lane in Sprint Qualifying until the start of the Sprint (or end of SQ1 if it never leaves)")
add_fact("B3.5.1", "parc fermé conditions", "APPLIES_DURING", "qualifying", context="from first leaving the pit lane in Qualifying until the start of the Race (or end of Q1 if it never leaves)")
add_fact("B3.5.2", "competitor", "REQUIRES", "suspension set-up sheet", context="given to the technical delegate before each car first leaves the pit lane in Sprint Qualifying and Qualifying")
add_fact("B3.5.3", "technical delegate", "CONTROLS", "parc fermé conditions", context="only Appendix B2 work or work they approve; no part replaced or setup changed otherwise")
add_fact("B3.5.3", "parc fermé breach", "PUNISHABLE_BY", "pit lane start", context="SFC: start the Race from the pit lane")
add_fact("B3.5.3", "parc fermé breach", "PUNISHABLE_BY", "pit lane start", context="AFC: start the Sprint from the pit lane if breached before the Sprint, the Race if breached after the start of Qualifying")
add_fact("B3.5.4", "technical delegate", "CONTROLS", "parc fermé conditions", context="approves other work after a written request; replacement parts must match design, mass, inertia and function")
add_fact("B3.5.4", "scrutineer", "CONTROLS", "parc fermé conditions", context="removed or broken parts must stay in full view of the car's scrutineer")
add_fact("B3.5.5", "parc fermé conditions", "REQUIRES", "front wing bodywork", "rear wing bodywork", "rear bodywork", "floor bodywork",
  context="six times per Championship a replacement of different design may be approved if already used in public testing, SQ, Qualifying or a TTCS")
add_fact("B3.5.6", "fia", "CONTROLS", "f1 car", context="selects cars for further checks after Sprint Qualifying and Qualifying; they go to parc fermé immediately")
add_fact("B3.5.7", "parc fermé conditions", "REQUIRES", "front wing bodywork", context="suspension and aero settings (except the front wing) must be impossible to change without tools")
add_fact("B3.5.8", "scrutineer", "CONTROLS", "parc fermé conditions", context="one scrutineer per car to prevent unauthorised work")
add_fact("B3.5.8", "competitor", "REQUIRES", "parc fermé camera", context="one per car, directly above it in the designated garage area; uncovered and operational throughout the Competition")
add_fact("B3.5.8", "parc fermé camera", "OCCURS_AT", "designated garage area")
add_fact("B3.5.8", "parc fermé camera", "DEFINED_IN", "fia-f1-doc-079")
add_fact("B3.6.1", "official", "CONTROLS", "parc fermé", context="only supervising officials may enter; no intervention without their authorisation")
add_fact("B3.6.2", "parc fermé conditions", "OCCURS_AT", "control line", context="apply from the control line to the parc fermé entrance")
add_fact("B3.6.3", "official", "CONTROLS", "parc fermé", context="secured; max three team personnel per car, only to fit cooling fans or do work the officials require")
add_fact("B3.6.4", "driver", "REQUIRES", "helmet", context="must stay fully attired until weighed")
build("B3", MENTIONS)
