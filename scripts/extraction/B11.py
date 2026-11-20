"""Entity/relationship extraction for Article B11 (Track Running Outside A Competition). Writes data/extractions/B11.json."""

from common import *
TCC, TPC, TMC, THC = "testing of current car", "testing of previous car", "testing of mule car", "testing of historic car"
PE, DE, OOC, PST = "promotional event", "demonstration event", "out-of-competition tyre testing", "post-season test"
PRIV, PUB, SDT = "pre-season private collective testing", "pre-season public collective testing", "substitute driver test"
MENTIONS = {
"B11.1.1": ["competitor", "fia", TPC, PE, DE, "driver", "circuit"],
"B11.1.2": ["fia observer", TPC, PE, DE, "competitor", "circuit"],
"B11.2.1": [TCC, "tyre supplier", "fia", "competitor", OOC, "circuit", "championship", "competition"],
"B11.2.2": [TCC, OOC, "current car", "previous car", "mule car", "track"],
"B11.2.3": [TCC, "f1 car", "driver", "super licence", "rear light", "track"],
"B11.2.4": [TCC, "red flag"],
"B11.2.5": [TCC, "refuelling"],
"B11.2.6": [TCC, "appendix h of the isc", ISC],
"B11.2.7": [TCC, PRIV, PUB, PST, OOC, SDT, "competitor", "commercial rights holder", "fia", "f1 car", "pit lane", "covering of components",
            "floor bodywork", "wet-weather tyre", "tyre supplier", "competition", "championship", "circuit", "technical regulations", "super licence",
            "young driver", "fia international a licence", "power unit", "race", "replacement driver", "driver", "tyre"],
"B11.3.1": [TPC],
"B11.3.2": [TPC, "previous car", "competition", TCC, "championship"],
"B11.3.3": ["fia", TPC, "competitor"],
"B11.3.4": ["competitor", TPC],
"B11.3.5": [TPC, "fia grade 1 circuit", "circuit", "competition", "championship", "fia"],
"B11.3.6": ["competitor", TPC],
"B11.3.7": ["competitor", TPC, "driver", "championship", "replacement driver"],
"B11.3.8": [TPC, "tyre", "tyre supplier"],
"B11.4.1": [TMC, "mule car", "fia", "tyre", "championship"],
"B11.4.2": [TMC, "competitor", "fia", "tyre supplier"],
"B11.4.3": [TMC, "red flag"],
"B11.4.4": [TMC, "refuelling"],
"B11.4.5": [TMC, "mule car", "current car", "previous car", "track"],
"B11.4.6": [TMC, "appendix h of the isc", ISC],
"B11.4.7": [TMC, "fia grade 1 circuit", "track"],
"B11.4.8": ["fia", TMC, "mule car", "competitor"],
"B11.4.9": [TMC, "tyre", "tyre supplier", "fia", "championship"],
"B11.4.10": ["fia", "competitor", "tyre supplier", TMC, "driver", "super licence", "competition", "championship", "circuit", "mule car", "f1 car", TCC, "race"],
"B11.4.11": [TMC, "mule car", "competitor", "fia", TCC, TPC, "tyre supplier", "tyre"],
"B11.5.1": [THC, "historic car"],
"B11.5.2": [THC, "tyre", "tyre supplier"],
"B11.6.1": ["competitor", PE, "current car", TCC],
"B11.6.2": [PE, "competitor"],
"B11.6.3": [PE, "tyre", "tyre supplier"],
"B11.7.1": ["fia", "competitor", DE, "current car", TCC, "commercial rights holder"],
"B11.7.2": [DE, "current car"],
"B11.7.3": [DE, "previous car"],
"B11.7.4": [DE, "fia standard ecu", "technical regulations"],
"B11.7.5": [DE, "tyre", "tyre supplier"],
"B11.8.1": ["competitor", TCC, TPC, TMC, PE, "technical regulations", "driver", "team personnel", "marshal", "fia", "f1 car", "fia standard ecu"],
"B11.8.2": [TCC, TPC, TMC, "impact warning light", "driver", "medical centre", "medical examination"],
"B11.8.3": [PST, OOC, "fia", "competitor", TPC, "technical regulations", "competition", TCC, "tyre"],
"B11.8.4": [PST, TPC, OOC, "tyre supplier"],
"B11.8.5": ["young driver", "f1 car", PST, TPC, "competitor", OOC, "tyre supplier", "fia", "tyre"],
}
add_fact("B11.1.1", "competitor", "REPORTS_TO", "fia", context="declare any planned TPC, PE or DE to the FIA and all Competitors at least 7 days before (amendable until 72 h): cars, drivers, type, dates, purpose, venue")
add_fact("B11.1.2", "fia observer", "APPLIES_DURING", TPC, PE, DE, context="may be appointed to attend; the Competitor must arrange access")
add_fact("B11.2.1", TCC, "OCCURS_AT", "circuit", context="09:00-19:00, max 9 h continuous; circuits in Europe unless most Competitors and the FIA agree (or for tyre testing); never during a Competition")
add_fact("B11.2.2", TCC, "REQUIRES", "current car", context="no other type of car on track")
add_fact("B11.2.2", OOC, "REQUIRES", "current car", "previous car", "mule car", context="only these types on track")
add_fact("B11.2.3", "f1 car", "REQUIRES", "rear light", context="TCC: blue main rear light lit at all times if the driver doesn't qualify for a Super Licence")
for t, c in [(PRIV, "one 5-day test between 5 and 31 Jan 2026; three running days per Competitor; one car per day"),
             (PUB, "two 3-day tests from 7 Feb to 7 days before the first Competition; one car per day; a wet-tyre day possible"),
             (PST, "one day at the last Competition's circuit, at least 36 h after it; two Section C cars: one tyre-test car, one young-driver car"),
             (OOC, "max 40 car days organised by the FIA with the Competitors and the Tyre Supplier"),
             (SDT, "one day for a new driver with no F1 race in the previous two years; within 14 days of the substitution; not at a current-season circuit; one car")]:
    add_fact("B11.2.7", TCC, "HAS_PART", t, context=c)
add_fact("B11.2.7", "covering of components", "APPLIES_DURING", PUB, context="B3.3 cover rules apply, except when the floor is off or while repairing a damaged car")
add_fact("B11.2.7", PST, "REQUIRES", "super licence", context="tyre-test car driven by drivers holding or qualifying for a Super Licence")
add_fact("B11.2.7", PST, "REQUIRES", "young driver", context="second car for young drivers: FIA International A Licence and no more than two F1 races")
add_fact("B11.2.7", "young driver", "REQUIRES", "fia international a licence")
add_fact("B11.2.7", OOC, "REQUIRES", "super licence", context="Full Super Licence eligibility plus one F1 Competition or 500 km in a recent car at racing speed")
add_fact("B11.2.7", "fia", "CONTROLS", OOC, context="organised for the Tyre Supplier to test design improvements; at a current-season circuit only after its Competition")
add_fact("B11.2.7", SDT, "REQUIRES", "replacement driver", context="if the new driver then isn't entered, the Competitor loses one pre-season TCC day next year")
add_fact("B11.3.2", TPC, "REQUIRES", "previous car", context="built to the period's specification, with components/software already used in a Competition or TCC of that period")
add_fact("B11.3.3", "fia", "CONTROLS", TPC, context="may approve non-compliant components or software for cost, reliability, safety, availability or track reasons, on formal request")
add_fact("B11.3.5", TPC, "OCCURS_AT", "fia grade 1 circuit", context="not at a current-season circuit within 60 days of its Competition, nor one missing from last year's calendar or significantly modified")
add_fact("B11.3.7", TPC, "APPLIES_DURING", "championship", context="max 20 days a year; max 1000 km a year with current or intended race drivers, over at most four days; replacements count as the original")
add_fact("B11.3.8", "tyre supplier", "ALLOCATES", "tyre", context="TPC: only tyres made specifically for it")
add_fact("B11.4.1", "fia", "CONTROLS", "mule car", context="TMC cars limited to the minimal modifications needed to test development tyres or FIA components")
add_fact("B11.4.2", "fia", "CONTROLS", TMC, context="09:00-19:00 unless all participants, the FIA and the Tyre Supplier agree; max 9 h continuous")
add_fact("B11.4.5", TMC, "REQUIRES", "mule car", "current car", "previous car", context="only these types on track")
add_fact("B11.4.7", TMC, "OCCURS_AT", "fia grade 1 circuit")
add_fact("B11.4.8", "fia", "CONTROLS", TMC, context="may approve components/software outside the Mule Car definition, on formal request")
add_fact("B11.4.9", "tyre supplier", "ALLOCATES", "tyre", context="TMC: development tyres for next season, or tyres the FIA and supplier agree on")
add_fact("B11.4.10", "fia", "CONTROLS", TMC, context="max 10 car days a year, organised with the Competitors and, if needed, the Tyre Supplier")
add_fact("B11.4.10", TMC, "REQUIRES", "super licence", context="Full Super Licence eligibility plus one F1 Competition or 500 km in a current car at racing speed")
add_fact("B11.4.10", TMC, "OCCURS_AT", "circuit", context="before that circuit's Competition only with a previous-four-years car, a driver not entered in the Championship (within 60 days), and a circuit on last year's calendar")
add_fact("B11.4.10", TMC, "REQUIRES", "mule car", context="1 Jan to the first Competition: previous-four-years mule car; after it: current-regs or previous-four-years mule car")
add_fact("B11.4.11", "fia", "CONTROLS", "mule car", context="no parts or software giving unrelated information; changes only if needed for the test and approved by the FIA")
add_fact("B11.4.11", "tyre supplier", "CONTROLS", TMC, context="when tyres are tested: set-up changes and sensors agreed with the supplier and the FIA; sensor data shared with the supplier")
add_fact("B11.5.1", THC, "REQUIRES", "historic car", context="built to the period's specification")
add_fact("B11.5.2", "tyre supplier", "ALLOCATES", "tyre", context="THC: tyres made for it, or tyres of the period")
add_fact("B11.6.1", PE, "REQUIRES", "current car", context="two PEs per Competitor; not counted as TCC")
add_fact("B11.6.3", "tyre supplier", "ALLOCATES", "tyre", context="PE: only tyres made specifically for it")
add_fact("B11.7.1", "fia", "CONTROLS", DE, context="at its discretion: two DEs per Competitor with a Current Car, plus CRH-organised DEs; not counted as TCC")
add_fact("B11.7.1", DE, "REQUIRES", "current car")
add_fact("B11.7.2", DE, "REQUIRES", "current car", context="max 15 km per event")
add_fact("B11.7.3", DE, "REQUIRES", "previous car", context="max 50 km per event")
add_fact("B11.7.4", DE, "REQUIRES", "fia standard ecu", context="Article C8.2")
add_fact("B11.7.5", "tyre supplier", "ALLOCATES", "tyre", context="DE: only tyres made specifically for it")
for t in [TCC, TPC, TMC, PE]:
    add_fact("B11.8.1", t, "REQUIRES", "fia standard ecu")
    add_fact("B11.8.1", t, "REQUIRES", "technical regulations", context="cars passed the static and dynamic tests and meet all safety requirements of the relevant year; sensor exceptions notified 7 days ahead")
add_fact("B11.8.2", "medical examination", "OCCURS_AT", "medical centre", context="after an incident in TCC, TPC or TMC that activates the Impact Warning Light, without delay")
add_fact("B11.8.3", "fia", "CONTROLS", PST, OOC, context="no test parts giving unrelated information; component/software changes only if needed for the tyre test and approved")
add_fact("B11.8.3", "fia", "CONTROLS", TPC, context="no parts, sensors or tests giving information about current-Championship cars")
add_fact("B11.8.4", "tyre supplier", "CONTROLS", OOC, context="set-up and driver control changes only if needed for the tyre test, agreed in advance")
add_fact("B11.8.5", "tyre supplier", "CONTROLS", PST, OOC, context="tyre-test car: extra sensors only for tyre state, agreed with the supplier and the FIA; data shared with the supplier")
add_fact("B11.8.5", "fia", "CONTROLS", TPC, context="extra logging and sensors prohibited, as on the post-season young-driver car")
build("B11", MENTIONS)
