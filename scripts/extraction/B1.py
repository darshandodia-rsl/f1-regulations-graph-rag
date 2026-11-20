"""Entity/relationship extraction for Article B1 (Organisation Of A Competition). Writes data/extractions/B1.json."""

from common import *

MENTIONS = {  # clause -> entities mentioned
"B1.1.1": ["competition", "fp1", ISC],
"B1.1.2": ["steward", "race director", "competitor", "circular", ISC, "free practice", "sprint qualifying", "sprint", "qualifying", "race", "classification", "official", "document management system"],
"B1.1.3": ["fia", "circuit", "competition", "free practice", "sprint qualifying", "qualifying", "race", "pit lane exit", "f1 car", "reconnaissance lap"],
"B1.1.4": ["competitor", "track"],
"B1.1.5": ["race director", "chief medical officer", "medical delegate", "driver", "medical examination", "competition", "impact warning light", "competition medical service"],
"B1.2.1": ["fia", "competition", "fia delegate", "safety delegate", "sporting delegate", "medical delegate", "media delegate", "technical delegate", "fia president representative", "event observer", "safety car driver", "deputy race director", "medical car driver", "deputy medical delegate"],
"B1.2.2": ["fia delegate", "official", "competition", "championship", REGS],
"B1.2.3": ["technical delegate", "fia", "scrutineering", "scrutineer", "f1 car", "competition", "steward", "clerk of the course"],
"B1.3.1": ["super licence", "official", "fia", "steward", "chair of the stewards", "race director", "permanent starter"],
"B1.3.2": ["super licence", "official", "asn", "fia", "steward", "clerk of the course", "competition"],
"B1.3.3": ["clerk of the course", "race director", "free practice", "qualifying", "sprint qualifying", "sprint", "race", "steward", ISC, REGS, "f1 car", "session interruption", "suspension", "resumption procedure", "start procedure", "safety car"],
"B1.3.4": ["steward", "race director", "clerk of the course", "technical delegate", "competition"],
"B1.3.5": ["steward", "competition"],
"B1.3.6": ["race director", "clerk of the course", "chair of the stewards", "f1 car", "track", "race control", "marshal post"],
"B1.3.7": ["steward", "judge of fact"],
"B1.4.1": ["alternative format competition", "official meeting", "race director", "fp1", "sprint qualifying", "team manager", "driver"],
"B1.4.2": ["standard format competition", "official meeting", "race director", "fp1", "fp2", "team manager", "driver"],
"B1.4.3": ["race director", "official meeting", "race", "competitor", "driver", "team manager"],
"B1.5.1": ["pit lane", "track", "free practice", "qualifying", "sprint qualifying", "sprint", "race", REGS],
"B1.5.2": ["f1 car", "track", "marshal", "competitor", "driver", "unnecessary stop on track"],
"B1.5.3": [ISC, REGS, "driver", "f1 car", "paddock", "designated garage area", "pit lane", "starting grid"],
"B1.5.4": ["free practice", "qualifying", "sprint qualifying", "formation lap", "sprint", "race", "f1 car", "parc fermé", "track", "pit entry road", "pit exit road", "marshal", "driver", "team personnel", "starting grid", TT],
"B1.5.5": ["rear light", "lateral light", "technical regulations", "intermediate tyre", "wet-weather tyre", "f1 car", "pit lane", LT, TT, "race director", "driver"],
"B1.5.6": ["organiser", "fire extinguisher", "competitor"],
"B1.5.7": ["fia", "track", "pit lane", "paddock"],
"B1.5.8": ["team personnel", "competitor", "signalling area", "free practice", "qualifying", "sprint qualifying", "sprint", "race"],
"B1.5.9": ["refuelling", "designated garage area", "f1 car", "driver", "internal combustion engine", "team personnel", "flame-resistant clothing", "fire extinguisher"],
"B1.5.10": ["heat hazard", "official weather service", "sprint", "race", "race director", "competition", "driver cooling system", "driver", "technical regulations"],
"B1.5.11": ["low grip conditions", "normal grip conditions", "race director", "low grip conditions message", "normal grip conditions message", "competitor", "sprint qualifying", "qualifying"],
"B1.6.1": ["fia", "designated garage area", "pit lane", "competitor", "designated pit stop position", "pit stop", "race director", "fast lane", "inner lane", "f1 car", "pit stop camera", TT, "fia-f1-doc-079"],
"B1.6.2": ["designated garage area", "designated pit stop position", "pit stop", "f1 car", "competitor", "team personnel", "driver", "unsafe release", LT, TT, "steward", "grid place penalty", "race", "sprint qualifying", "sprint", SG, "fine", "penalty", "pit lane", "parc fermé", "chequered flag", "race director", "pit lane access message", "helmet", "qualifying", "free practice", "reconnaissance lap", "pit lane exit"],
"B1.6.3": ["pit entry road", "pit lane", "pit exit road", "competition", "race director", "competitor", "driver", "pit lane speeding", "free practice", "qualifying", "sprint qualifying", "fine", "steward", "penalty", TT, S5, S10, DT, SG, "f1 car", "designated pit stop position", "track", "designated garage area", "pit lane exit", "starting grid", "start procedure", LT, "fast lane", "pit exit light", "blue flag", "pit exit road"],
"B1.6.4": ["race director", "pit lane closure", "pit entry road", "driver", "pit lane", "f1 car", LT, TT, "penalty", "steward", "entering a closed pit lane", SG],
"B1.7.1": ["championship", "competitor", "driver", "race", "replacement driver"],
"B1.7.2": ["change of driver", "scrutineering", "steward", "competition", "sprint", "qualifying", "sprint qualifying", "race", "driver"],
"B1.7.3": ["young driver", "fp1", "fp2", "competition", "championship", "f1 car", "competitor", "race", "power unit", "tyre", "super licence", "free practice super licence", "pit lane", "fia", "driver"],
"B1.7.4": ["additional driver", "competitor", "fp1", "fp2", "fia", "f1 car", "steward", "driver", "change of driver"],
"B1.7.5": ["competitor", "driver", "scrutineering", "steward", "change of driver", "replacement driver", "power unit", "tyre"],
"B1.8.1": ["driver", "f1 car"],
"B1.8.2": ["driver", "flame-resistant clothing", "helmet", "frontal head restraint", ISC],
"B1.8.3": ["driver", ISC, "circuit"],
"B1.8.4": ["driver", ISC, "competitor", "appendix h of the isc", "fia light panel", "grid light panel", "fia standard ecu", "waved yellow flag", "double waved yellow flag", "marshalling sector", "steward", "lap time deletion", "safety car period", "virtual safety car", "start procedure", "standing start resumption"],
"B1.8.5": ["f1 car", "erratic driving", "driver"],
"B1.8.6": ["driver", "track", "leaving the track", "f1 car", "race director"],
"B1.8.7": ["driver", "track", "pit lane", "competitor", "race director", "f1 car", "competition"],
"B1.8.8": ["driver", "f1 car", "ers", "marshal", "circuit"],
"B1.8.9": [TT, "suspension", "f1 car", "circuit", "driver"],
"B1.9.1": ["race director", "incident", "steward", REGS, ISC],
"B1.9.2": ["steward", "investigation", "incident", "competitor", "driver", "chequered flag", TT, "circuit"],
"B1.9.3": ["steward", "driver", "incident", "penalty", REGS, ISC],
"B1.9.4": ["incident", LT, "steward", "driver", "lap time deletion", "grid place penalty", "driving infringement", "race", "sprint qualifying", "sprint", "starting grid"],
"B1.9.5": ["incident", TT, "steward", "driver", S5, S10, DT, SG, "pit lane", "designated pit stop position", "time penalty", "driver reprimand", "driving infringement", "grid place penalty", "race", "competition", "championship", "competitor reprimand", "competitor", "sprint", "disqualification", "suspension from next competition"],
"B1.9.6": ["steward", S5, S10, DT, SG, "competitor", "official messaging system", "pit lane", "safety car", "suspension", "red flag", "designated garage area", "designated pit stop position", "virtual safety car", "safety car period", TT, "f1 car", "driver", "control line", "pit entry road", "grid place penalty", "race", "penalty", "pit stop", "time penalty"],
"B1.9.7": ["appeal", "penalty", "grid place penalty", "steward", TT],
}


add_fact("B1.1.2", "classification", "REQUIRES", "document management system", context="all classifications, results and decisions are published on the DMS")
add_fact("B1.1.2", "circular", "DEFINED_IN", ISC)
add_fact("B1.1.3", "fia", "CONTROLS", "circuit", context="written permission needed to use the circuit for other purposes during the Competition")
for o in ["race director", "chief medical officer", "medical delegate"]:
    add_fact("B1.1.5", o, "CONTROLS", "medical examination", context="may require a driver to be examined at any time during a Competition")
add_fact("B1.1.5", "competition medical service", "CONTROLS", "medical examination", context="examines the driver without delay after an incident that activates the Impact Warning Light")
add_fact("B1.2.1", "fia", "APPOINTS", "safety delegate", "sporting delegate", "medical delegate", "media delegate", "technical delegate",
  context="mandatory for each Competition")
add_fact("B1.2.1", "fia", "APPOINTS", "fia president representative", "event observer", "safety car driver", "deputy race director",
  "medical car driver", "deputy medical delegate", context="optional (may nominate)")
for o in ["safety delegate", "sporting delegate", "medical delegate", "media delegate", "technical delegate"]:
    add_fact("B1.2.1", o, "TYPE_OF", "fia delegate")
add_fact("B1.2.3", "technical delegate", "CONTROLS", "scrutineering", context="any checks at any time until the end of the Competition, without a request from the stewards or clerk of the course")
add_fact("B1.2.3", "technical delegate", "CONTROLS", "scrutineer", context="full authority over the national scrutineers")
add_fact("B1.3.1", "fia", "APPOINTS", "steward", context="three or four stewards, one of whom is appointed chair")
add_fact("B1.3.1", "fia", "APPOINTS", "race director", "permanent starter")
add_fact("B1.3.1", "chair of the stewards", "TYPE_OF", "steward")
for o in ["steward", "race director", "permanent starter"]:
    add_fact("B1.3.1", o, "REQUIRES", "super licence", context="nominated from among FIA Super Licence holders")
add_fact("B1.3.2", "asn", "APPOINTS", "steward", context="one steward from among the ASN's nationals")
add_fact("B1.3.2", "asn", "APPOINTS", "clerk of the course")
add_fact("B1.3.2", "steward", "REQUIRES", "super licence", context="nominated from among FIA Super Licence holders")
add_fact("B1.3.2", "clerk of the course", "REQUIRES", "super licence", context="nominated from among FIA Super Licence holders")
add_fact("B1.3.3", "clerk of the course", "REPORTS_TO", "race director", context="works in permanent consultation with the race director")
add_fact("B1.3.3", "race director", "CONTROLS", "free practice", "qualifying", "sprint qualifying", "sprint", "race",
  "session interruption", "suspension", "resumption procedure", "start procedure", "safety car",
  context="overriding authority; the clerk of the course may give orders on these only with the race director's agreement")
add_fact("B1.3.6", "race director", "REPORTS_TO", "clerk of the course", "chair of the stewards", context="radio contact at all times when cars may run on track")
add_fact("B1.3.7", "steward", "CONTROLS", "judge of fact", context="may overrule judges of fact")
add_fact("B1.4.1", "race director", "CONTROLS", "official meeting", context="chairs the meetings")
add_fact("B1.4.1", "official meeting", "APPLIES_DURING", "alternative format competition", context="3 h before FP1, 1 h after FP1 and 1.5 h after Sprint Qualifying")
add_fact("B1.4.1", "team manager", "REQUIRES", "official meeting", context="AFC: all three meetings")
add_fact("B1.4.1", "driver", "REQUIRES", "official meeting", context="AFC: the meetings after FP1 and after Sprint Qualifying")
add_fact("B1.4.2", "race director", "CONTROLS", "official meeting", context="chairs the meetings")
add_fact("B1.4.2", "official meeting", "APPLIES_DURING", "standard format competition", context="3 h before FP1 and 1.5 h after FP2")
add_fact("B1.4.2", "team manager", "REQUIRES", "official meeting", context="SFC: both meetings")
add_fact("B1.4.2", "driver", "REQUIRES", "official meeting", context="SFC: the meeting after FP2")
add_fact("B1.4.3", "race director", "CONTROLS", "official meeting", context="may call an extra meeting 3 h before the Race")
add_fact("B1.4.3", "driver", "REQUIRES", "official meeting", context="extra meeting before the Race, if called")
add_fact("B1.4.3", "team manager", "REQUIRES", "official meeting", context="extra meeting before the Race, if called")
add_fact("B1.5.5", "f1 car", "REQUIRES", "rear light", context="illuminated whenever intermediate or wet-weather tyres are used; working when first leaving the pit lane in any LTCS or TTCS")
add_fact("B1.5.5", "f1 car", "REQUIRES", "lateral light", context="working when first leaving the pit lane in any LTCS or TTCS")
add_fact("B1.5.5", "rear light", "DEFINED_IN", "technical regulations")
add_fact("B1.5.5", "lateral light", "DEFINED_IN", "technical regulations")
add_fact("B1.5.5", "race director", "CONTROLS", "f1 car", context="decides whether to stop a car whose central rear light and a side light are not working")
add_fact("B1.5.6", "organiser", "ALLOCATES", "fire extinguisher", context="at least two 5 kg extinguishers per Competitor")
add_fact("B1.5.9", "refuelling", "OCCURS_AT", "designated garage area", context="only in the Competitor's designated garage; max 0.8 litres per second; engine stopped")
add_fact("B1.5.9", "refuelling", "REQUIRES", "flame-resistant clothing", context="outer garments to FIA Standard 8867-2016, 8856-2000 or 8856-2018")
add_fact("B1.5.9", "refuelling", "REQUIRES", "fire extinguisher", context="an assistant with a suitable extinguisher must be present")
add_fact("B1.5.10", "race director", "CONTROLS", "heat hazard", context="declared 24 h before the Competition if the Heat Index is forecast above 31.0°C, or at the race director's discretion")
add_fact("B1.5.10", "heat hazard", "APPLIES_DURING", "sprint", "race")
add_fact("B1.5.10", "heat hazard", "REQUIRES", "driver cooling system", context="all components fitted; a driver may skip the personal-equipment parts but must carry 0.5 kg ballast")
add_fact("B1.5.10", "driver cooling system", "DEFINED_IN", "technical regulations")
add_fact("B1.5.11", "race director", "CONTROLS", "low grip conditions", context="at any time, at their sole discretion")
add_fact("B1.5.11", "race director", "CONTROLS", "normal grip conditions", context="only after Low Grip Conditions were declared")
add_fact("B1.5.11", "low grip conditions message", "SIGNALS", "low grip conditions")
add_fact("B1.5.11", "normal grip conditions message", "SIGNALS", "normal grip conditions")
add_fact("B1.5.11", "normal grip conditions", "APPLIES_DURING", "sprint qualifying", "qualifying", context="may only be declared with more than 5 minutes left in a period")
add_fact("B1.6.1", "fia", "ALLOCATES", "designated garage area", "designated pit stop position", "pit stop camera", context="on an equal basis to each Competitor")
add_fact("B1.6.1", "pit stop", "OCCURS_AT", "designated pit stop position")
add_fact("B1.6.1", "competitor", "REQUIRES", "pit stop camera", context="installed directly above the designated pit stop position")
add_fact("B1.6.1", "pit stop camera", "DEFINED_IN", "fia-f1-doc-079")
add_fact("B1.6.1", "pit stop camera", "APPLIES_DURING", TT, context="must be uncovered and operational")
add_fact("B1.6.2", "unsafe release", "PUNISHABLE_BY", "grid place penalty", context="during an LTCS; applied to the Race, or to the Sprint if committed in Sprint Qualifying")
add_fact("B1.6.2", "unsafe release", "PUNISHABLE_BY", SG, context="during a TTCS")
add_fact("B1.6.2", "unsafe release", "PUNISHABLE_BY", "fine", context="during a TTCS, if the driver retires because of the unsafe release (fine on the Competitor)")
add_fact("B1.6.2", "unsafe release", "PUNISHABLE_BY", "penalty", context="additional penalty if the driver keeps driving knowing the car was released unsafely")
add_fact("B1.6.2", "steward", "MAY_IMPOSE", "grid place penalty", context="unsafe release during an LTCS")
add_fact("B1.6.2", "steward", "MAY_IMPOSE", "penalty", context="additional penalty for continuing after an unsafe release")
add_fact("B1.6.2", "unsafe release", "APPLIES_DURING", LT, TT)
add_fact("B1.6.2", "unsafe release", "OCCURS_AT", "designated pit stop position", "designated garage area")
add_fact("B1.6.2", "grid place penalty", "APPLIES_DURING", "race", context="unsafe release in an LTCS other than Sprint Qualifying")
add_fact("B1.6.2", "grid place penalty", "APPLIES_DURING", "sprint", context="unsafe release in Sprint Qualifying")
add_fact("B1.6.2", SG, "APPLIES_DURING", TT, context="unsafe release")
add_fact("B1.6.2", "team personnel", "REQUIRES", "helmet", context="when working on a car in its pit stop position during qualifying, sprint qualifying or a TTCS; eye protection also compulsory")
add_fact("B1.6.3", "race director", "CONTROLS", "pit lane", context="may amend the 80 km/h pit lane speed limit")
add_fact("B1.6.3", "pit lane speeding", "OCCURS_AT", "pit lane", context="80 km/h limit for the whole Competition unless amended")
add_fact("B1.6.3", "pit lane speeding", "PUNISHABLE_BY", "fine", context="during free practice, qualifying or sprint qualifying: €100 per km/h over the limit, max €1000 (on the Competitor)")
add_fact("B1.6.3", "pit lane speeding", "PUNISHABLE_BY", "penalty", context="additional penalty if the stewards suspect speeding to gain an advantage")
add_fact("B1.6.3", "pit lane speeding", "PUNISHABLE_BY", S5, S10, DT, SG, context="during a TTCS")
add_fact("B1.6.3", "steward", "MAY_IMPOSE", "penalty", context="additional penalty for pit lane speeding to gain an advantage")
add_fact("B1.6.3", "steward", "MAY_IMPOSE", S5, S10, DT, SG, context="pit lane speeding during a TTCS")
add_fact("B1.6.3", "fine", "APPLIES_DURING", "free practice", "qualifying", "sprint qualifying", context="pit lane speeding")
add_fact("B1.6.3", S5, "APPLIES_DURING", TT, context="pit lane speeding")
add_fact("B1.6.3", S10, "APPLIES_DURING", TT, context="pit lane speeding")
add_fact("B1.6.3", DT, "APPLIES_DURING", TT, context="pit lane speeding")
add_fact("B1.6.3", SG, "APPLIES_DURING", TT, context="pit lane speeding")
add_fact("B1.6.3", "pit lane", "HAS_PART", "fast lane")
add_fact("B1.6.4", "race director", "CONTROLS", "pit lane closure", context="in exceptional circumstances for safety; only cars needing essential repairs may then enter")
add_fact("B1.6.4", "entering a closed pit lane", "APPLIES_DURING", "pit lane closure", LT, TT)
add_fact("B1.6.4", "entering a closed pit lane", "PUNISHABLE_BY", "penalty", context="during an LTCS, penalty under B1.9.4, if entered without justifiable reason")
add_fact("B1.6.4", "entering a closed pit lane", "PUNISHABLE_BY", SG, context="during a TTCS")
add_fact("B1.6.4", "steward", "MAY_IMPOSE", "penalty", context="entering a closed pit lane during an LTCS")
add_fact("B1.6.4", "steward", "MAY_IMPOSE", SG, context="entering a closed pit lane during a TTCS")
add_fact("B1.7.2", "steward", "CONTROLS", "change of driver", context="consent required for changes after initial scrutineering")
add_fact("B1.7.2", "change of driver", "PRECEDES", "qualifying", context="for a driver taking part in the Race")
add_fact("B1.7.2", "change of driver", "PRECEDES", "sprint qualifying", context="at an AFC, for a driver taking part in the Sprint")
add_fact("B1.7.3", "young driver", "TYPE_OF", "driver", context="no more than two Championship Races; must be used in FP1 or FP2 at two Competitions per car")
add_fact("B1.7.3", "young driver", "REQUIRES", "super licence", "free practice super licence", context="either licence is sufficient")
add_fact("B1.7.3", "young driver", "REQUIRES", "power unit", "tyre", context="those allocated to the nominated driver being replaced")
add_fact("B1.7.4", "steward", "CONTROLS", "change of driver", context="changes less than 2 h before FP1")
add_fact("B1.7.4", "additional driver", "TYPE_OF", "driver", context="extra drivers in FP1 and FP2; max two per session; FIA informed 24 h before FP1")
add_fact("B1.7.5", "steward", "CONTROLS", "change of driver", context="replacing a nominated driver after initial scrutineering")
add_fact("B1.7.5", "replacement driver", "REQUIRES", "power unit", "tyre", context="those allocated to the original driver")
add_fact("B1.7.5", "replacement driver", "TYPE_OF", "driver")
add_fact("B1.8.2", "driver", "REQUIRES", "flame-resistant clothing", "helmet", "frontal head restraint", context="in any session")
add_fact("B1.8.2", "frontal head restraint", "DEFINED_IN", ISC)
add_fact("B1.8.3", "driver", "REQUIRES", ISC, context="driving behaviour on circuits")
add_fact("B1.8.4", "waved yellow flag", "DEFINED_IN", "appendix h of the isc")
add_fact("B1.8.4", "double waved yellow flag", "DEFINED_IN", "appendix h of the isc")
add_fact("B1.8.4", "fia light panel", "DEFINED_IN", "appendix h of the isc", context="light signals have the same meaning as flags")
add_fact("B1.8.7", "race director", "CONTROLS", "f1 car", context="may instruct a car with significant damage or failure to leave the track")
add_fact("B1.9.1", "race director", "REPORTS_TO", "steward", context="reports incidents and suspected breaches")
add_fact("B1.9.2", "steward", "CONTROLS", "investigation", context="at their discretion; drivers named within 60 min of the end of a TTCS may not leave the circuit without consent")
add_fact("B1.9.3", "steward", "MAY_IMPOSE", "penalty", context="only if a driver was wholly or predominantly to blame")
add_fact("B1.9.3", "incident", "PUNISHABLE_BY", "penalty", context="only if a driver was wholly or predominantly to blame")
add_fact("B1.9.3", "penalty", "DEFINED_IN", ISC, REGS)
add_fact("B1.9.4", "steward", "MAY_IMPOSE", "lap time deletion", "grid place penalty", context="incident during an LTCS")
add_fact("B1.9.4", "incident", "PUNISHABLE_BY", "lap time deletion", "grid place penalty", context="during an LTCS")
add_fact("B1.9.4", "lap time deletion", "APPLIES_DURING", LT)
add_fact("B1.9.4", "grid place penalty", "APPLIES_DURING", "race", context="LTCS incident other than in Sprint Qualifying")
add_fact("B1.9.4", "grid place penalty", "APPLIES_DURING", "sprint", context="incident in Sprint Qualifying")
add_fact("B1.9.4", "driving infringement", "TYPE_OF", "incident")
P95 = [S5, S10, DT, SG, "time penalty", "competitor reprimand", "disqualification", "suspension from next competition"]
add_fact("B1.9.5", "steward", "MAY_IMPOSE", *P95, context="incident during a TTCS")
add_fact("B1.9.5", "incident", "PUNISHABLE_BY", *P95, context="during a TTCS")
add_fact("B1.9.5", "steward", "MAY_IMPOSE", "driver reprimand", context="incident during a TTCS; a fifth reprimand in a Championship (at least four for driving) brings a 10-place grid penalty")
add_fact("B1.9.5", "incident", "PUNISHABLE_BY", "driver reprimand", context="during a TTCS")
add_fact("B1.9.5", "steward", "MAY_IMPOSE", "grid place penalty", context="incident during a TTCS; for the next Sprint or Race within 12 months")
add_fact("B1.9.5", "incident", "PUNISHABLE_BY", "grid place penalty", context="during a TTCS")
for p in [S5, S10, SG]:
    add_fact("B1.9.5", p, "TYPE_OF", "time penalty")
add_fact("B1.9.5", S5, "OCCURS_AT", "designated pit stop position", context="stop for at least 5 s")
add_fact("B1.9.5", S10, "OCCURS_AT", "designated pit stop position", context="stop for at least 10 s")
add_fact("B1.9.5", SG, "OCCURS_AT", "designated pit stop position", context="stop for at least 10 s")
add_fact("B1.9.5", DT, "OCCURS_AT", "pit lane", context="drive through without stopping")
for p in [S5, S10, DT, SG]:
    add_fact("B1.9.5", p, "APPLIES_DURING", TT)
add_fact("B1.9.6", "steward", "MAY_IMPOSE", "grid place penalty", context="when a 5 s, 10 s, drive-through or stop-and-go penalty cannot be served (unclassified or retired); applied at the next Race")
add_fact("B1.9.6", "grid place penalty", "APPLIES_DURING", "race", context="unserved TTCS time penalty; the driver's next Race")
add_fact("B1.9.6", "steward", "MAY_IMPOSE", "penalty", context="further penalty for failing to serve a penalty correctly; replaces the original")
for p in [S5, S10, DT, SG]:
    add_fact("B1.9.6", p, "REQUIRES", "official messaging system", context="all Competitors informed via the OMS")
add_fact("B1.9.6", S5, "OCCURS_AT", "pit lane", context="served at the next pit lane entry; if no further stop, 5 s added to elapsed time; car not worked on while stationary")
add_fact("B1.9.6", S10, "OCCURS_AT", "pit lane", context="served at the next pit lane entry; if no further stop, 10 s added to elapsed time; car not worked on while stationary")
add_fact("B1.9.6", DT, "OCCURS_AT", "pit lane", context="must enter within two crossings of the control line; 20 s added if imposed in the last three laps or after the session")
add_fact("B1.9.6", SG, "OCCURS_AT", "pit lane", context="must enter within two crossings of the control line; 30 s added if imposed in the last three laps or after the session")

build("B1", MENTIONS)
