"""Entity/relationship extraction for Article B6 (Tyre Limitations). Writes data/extractions/B6.json."""

from common import *
ICTT, ICTE = "in-competition tyre testing", "in-competition tyre evaluation"
DRY, INT, WET = "dry-weather tyre", "intermediate tyre", "wet-weather tyre"
MQ3, MR = "mandatory q3 tyre specification", "mandatory race tyre specification"
MENTIONS = {
"B6.1.1": ["tyre supplier", "fia", "competition", DRY, INT, WET, "track", SFC, ICTE, ICTT, "competitor"],
"B6.1.2": ["fia", "tyre supplier", "competitor", "competition", ICTT, "driver", MR, "race", SFC, MQ3, "q3", DRY, ICTE, "tyre"],
"B6.1.3": ["tyre", "fia", "tyre supplier", "fia-f1-doc-062", "competitor", "competition", "f1 car", "fia grade 1 circuit", "rim manufacturer"],
"B6.2.1": ["steward", "tyre", "competition", "technical delegate", "tyre allocation"],
"B6.2.2": ["tyre set", "tyre"],
"B6.2.3": ["technical delegate", "tyre set", "driver", "tyre supplier", "competition", "tyre allocation"],
"B6.2.4": ["fia", "tyre supplier", "competition", "tyre set", "driver", "tyre allocation", SFC, AFC, ICTT, DRY, "hard tyre", "medium tyre", "soft tyre", INT, WET],
"B6.2.5": ["tyre", "competition", "grid place penalty", "disqualification", "race"],
"B6.2.6": ["competition", "technical delegate", "tyre", "competitor", "driver", "tyre supplier"],
"B6.2.7": ["competitor", "tyre", "technical delegate"],
"B6.3.1": ["tyre set", "competition", "driver", "unallocated tyre use", TT, "control line", "pit lane", SG, "race"],
"B6.3.2": ["tyre", "pit lane", "f1 car", "transponder", "starting grid"],
"B6.3.3": ["tyre set", "fia", "qualifying"],
"B6.3.4": ["tyre set", "driver", "competition", SFC, AFC, ICTT, DRY, INT, WET, "additional driver", "replacement driver"],
"B6.3.5": ["free practice", INT, WET, "wet track declaration", "race director", DRY],
"B6.3.6": ["driver", INT, WET, "race", DRY, MR, "mandatory tyre specification breach", "disqualification", "suspension", "time penalty"],
"B6.3.7": ["formation lap behind safety car", TT, "resumption procedure", WET, "safety car orange lights", "safety car", "pit lane", SG, "driver", "tyre"],
"B6.3.8": [SFC, DRY, ICTT, "tyre set", "driver", MQ3, "q3", "sealing of cars", MR, "race", "tyre return", "fp1", "fp2", "fp3", "wet track declaration", INT, WET],
"B6.3.9": [AFC, DRY, "tyre set", "driver", "tyre return", "fp1", "sprint", "sealing of cars", "qualifying", "sprint qualifying", "sq1", "sq2", "sq3",
           "medium tyre", "soft tyre", INT, WET, "wet track declaration", "pit lane exit", "race"],
"B6.3.10": [SFC, ICTT, DRY, "tyre set", "driver", MQ3, "q3", "sealing of cars", MR, "race", "tyre return", "fp1", "fp2", "fp3", "medium tyre",
            "wet track declaration", INT, WET],
"B6.4.1": ["tyre return", "fia race team client", "fia", "competitor"],
"B6.4.2": ["tyre set", "tyre return", "tyre supplier"],
"B6.4.3": ["tyre", "tyre return", "tyre supplier", "driver", "competition"],
"B6.5.1": [DRY, INT, WET, "tyre allocation", SFC, ICTE, "tyre set", "driver"],
"B6.5.2": ["driver", "fp1", "fp2", ICTE, "tyre"],
"B6.5.3": [ICTE, "tyre return", "fp2"],
"B6.6.1": [DRY, "tyre allocation", SFC, ICTT, "tyre set", "driver"],
"B6.6.2": [ICTT, DRY, "driver", "fp2", "competition", "fia"],
"B6.6.3": [ICTT, "wet track declaration", "driver", "fp2", "tyre supplier", DRY],
"B6.6.4": ["driver", ICTT, "super licence", "competition"],
"B6.6.5": ["f1 car", "tyre supplier", "fia", "tyre", "competition", "testing of current car", ICTT],
"B6.6.6": ["f1 car", "tyre supplier", "fia", "competitor", "tyre", ICTT],
"B6.6.7": [ICTT, "tyre return", "fp2"],
}
add_fact("B6.1.1", "fia", "APPOINTS", "tyre supplier", context="single tyre manufacturer")
add_fact("B6.1.1", "tyre supplier", "ALLOCATES", DRY, context="three specifications per Competition, visibly distinguishable")
add_fact("B6.1.1", "tyre supplier", "ALLOCATES", INT, WET, context="one specification per Competition")
add_fact("B6.1.1", SFC, "HAS_PART", ICTE, context="at certain SFCs: one extra dry, intermediate or wet specification for evaluation")
add_fact("B6.1.1", SFC, "HAS_PART", ICTT, context="at most two SFCs (a third if one is unsuitable): extra dry specifications for testing")
add_fact("B6.1.2", "fia", "CONTROLS", MR, context="announced 2 weeks before the Competition; up to two specifications")
add_fact("B6.1.2", "fia", "CONTROLS", MQ3, context="SFC only; announced 2 weeks before; always the softest of the three specifications")
add_fact("B6.1.2", "fia", "CONTROLS", ICTT, context="announced 4 weeks before, with quantities and run plans")
add_fact("B6.1.2", "fia", "CONTROLS", ICTE, context="announced 1 week before")
add_fact("B6.1.2", MR, "TYPE_OF", DRY)
add_fact("B6.1.2", MQ3, "TYPE_OF", DRY)
add_fact("B6.1.3", "tyre", "DEFINED_IN", "fia-f1-doc-062", context="operated per FIA and Tyre Supplier prescriptions; not used on other rigs, simulators or vehicles")
add_fact("B6.2.1", "technical delegate", "CONTROLS", "tyre allocation", context="all tyres presented before the Competition, except force majeure accepted by the stewards")
add_fact("B6.2.2", "tyre set", "HAS_PART", "tyre", context="two front and two rear of the same specification")
add_fact("B6.2.3", "technical delegate", "ALLOCATES", "tyre set", context="to each driver from the Tyre Supplier's stock")
add_fact("B6.2.4", "tyre allocation", "APPLIES_DURING", SFC, AFC, ICTT, context="sets per driver of each specification depend on the format (table in B6.2.4)")
add_fact("B6.2.5", "grid place penalty", "APPLIES_DURING", "race", context="using tyres without the unique sidewall identification")
add_fact("B6.2.5", "disqualification", "APPLIES_DURING", "race", context="using tyres without the unique sidewall identification")
add_fact("B6.2.6", "technical delegate", "CONTROLS", "tyre", context="may pick alternative tyres for any Competitor from the supplier's stock at any time")
add_fact("B6.2.7", "technical delegate", "CONTROLS", "tyre", context="swapping an unused tyre for an identical one requires presenting both")
add_fact("B6.3.1", "unallocated tyre use", "PUNISHABLE_BY", SG, context="during a TTCS, if the tyres are not changed within two crossings of the control line")
add_fact("B6.3.1", "unallocated tyre use", "APPLIES_DURING", TT)
add_fact("B6.3.3", "tyre set", "APPLIES_DURING", "qualifying", context="used as complete sets; sets of the same specification may be mixed after Qualifying")
add_fact("B6.3.4", "additional driver", "REQUIRES", "tyre set", context="must use the tyres allocated to the nominated driver they replace")
add_fact("B6.3.4", "replacement driver", "REQUIRES", "tyre set", context="must use the tyres allocated to the nominated driver they replace")
add_fact("B6.3.5", INT, "APPLIES_DURING", "free practice", context="only after the track is declared wet")
add_fact("B6.3.5", WET, "APPLIES_DURING", "free practice", context="only after the track is declared wet")
add_fact("B6.3.5", "race director", "CONTROLS", "wet track declaration")
add_fact("B6.3.6", "race", "REQUIRES", DRY, context="at least two different dry specifications unless intermediate or wet tyres were used")
add_fact("B6.3.6", "race", "REQUIRES", MR, context="at least one of the dry specifications used must be a mandatory one")
add_fact("B6.3.6", "mandatory tyre specification breach", "PUNISHABLE_BY", "disqualification", context="from the Race results")
add_fact("B6.3.6", "mandatory tyre specification breach", "PUNISHABLE_BY", "time penalty", context="30 s added if the Race is suspended and not restarted")
add_fact("B6.3.7", "formation lap behind safety car", "REQUIRES", WET, context="when mandated: compulsory until the safety car's orange lights go out and it returns to the pit lane")
add_fact("B6.3.7", "resumption procedure", "REQUIRES", WET, context="when mandated at the ten minute signal: compulsory until the safety car returns to the pit lane")
add_fact("B6.3.7", SG, "APPLIES_DURING", "formation lap behind safety car", "resumption procedure", context="tyres changed to another specification while the safety car is on track")
add_fact("B6.3.8", MQ3, "APPLIES_DURING", "q3", context="SFC: one set may not be used or returned before Q3; Q3 cars return one set of it by covers-on time")
add_fact("B6.3.8", MR, "APPLIES_DURING", "race", context="two sets may not be returned before the Race (one of each if two specifications)")
add_fact("B6.3.8", "tyre return", "APPLIES_DURING", SFC, context="no ICTT: two dry sets returned within 2 h after FP1, two after FP2, two after FP3")
add_fact("B6.3.8", INT, "APPLIES_DURING", SFC, context="if FP1, FP2 or FP3 is declared wet, one intermediate set returned within 2 h after FP3")
add_fact("B6.3.9", "tyre return", "APPLIES_DURING", AFC, context="one dry set after FP1, one after the Sprint (the set with most Sprint laps), three by covers-on after Qualifying")
add_fact("B6.3.9", "medium tyre", "APPLIES_DURING", "sq1", "sq2", context="up to one new set in each period")
add_fact("B6.3.9", "soft tyre", "APPLIES_DURING", "sq3", context="up to one set")
add_fact("B6.3.9", INT, "APPLIES_DURING", AFC, context="max one extra set if FP1 or Sprint Qualifying is declared wet, or if the driver used intermediates in the Sprint")
add_fact("B6.3.10", "tyre return", "APPLIES_DURING", ICTT, context="SFC with ICTT: one dry set after FP1, a medium set kept for FP2 plus one more returned after FP2, two after FP3")
add_fact("B6.3.10", MQ3, "APPLIES_DURING", "q3", context="SFC with ICTT: one set may not be used or returned before Q3")
add_fact("B6.3.10", MR, "APPLIES_DURING", "race", context="SFC with ICTT: two sets may not be returned before the Race")
add_fact("B6.3.10", INT, "APPLIES_DURING", ICTT, context="if FP1, FP2 or FP3 is declared wet, one intermediate set returned within 2 h after FP3")
add_fact("B6.4.1", "tyre return", "REQUIRES", "fia race team client", context="electronic return; CSV by email if the system fails")
add_fact("B6.4.2", "tyre return", "REQUIRES", "tyre set", context="returned sets must also be physically returned to the Tyre Supplier before the next session")
add_fact("B6.4.3", "tyre supplier", "CONTROLS", "tyre return", context="publishes each driver's remaining tyres after each day")
add_fact("B6.5.1", "tyre allocation", "APPLIES_DURING", ICTE, context="max two sets of an extra evaluation specification per driver")
add_fact("B6.5.2", "tyre", "APPLIES_DURING", "fp1", "fp2", context="ICTE tyres may be used")
add_fact("B6.5.3", "tyre return", "APPLIES_DURING", ICTE, context="all ICTE tyres returned within 2 h after FP2")
add_fact("B6.6.1", "tyre allocation", "APPLIES_DURING", ICTT, context="extra sets of a test dry specification per driver")
add_fact("B6.6.2", DRY, "APPLIES_DURING", "fp2", context="ICTT test tyres must be used in FP2; moved to a back-up Competition if FP2 is unsuitable")
add_fact("B6.6.3", "tyre supplier", "CONTROLS", ICTT, context="drivers follow its run plans in FP2; only ICTT dry tyres may be used in FP2 unless declared wet")
add_fact("B6.6.4", ICTT, "REQUIRES", "super licence", context="drivers eligible for a Full Super Licence with at least one F1 Competition")
add_fact("B6.6.5", "fia", "CONTROLS", "f1 car", context="ICTT: component and software changes need FIA approval; car stays in a fixed specification")
add_fact("B6.6.5", "tyre supplier", "CONTROLS", "f1 car", context="ICTT: set-up and driver control changes agreed in advance with the Tyre Supplier")
add_fact("B6.6.6", "tyre supplier", "CONTROLS", ICTT, context="extra sensors agreed with the Tyre Supplier and the FIA; data shared with the supplier, may be passed on anonymised")
add_fact("B6.6.7", "tyre return", "APPLIES_DURING", ICTT, context="all ICTT tyres returned within 2 h after FP2")
build("B6", MENTIONS)
