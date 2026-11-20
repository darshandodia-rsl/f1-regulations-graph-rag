"""Entity/relationship extraction for Article B7 (Driver Adjustable Bodywork & Energy Deployment Limitations). Writes data/extractions/B7.json."""

from common import *
DAB, EDL = "driver adjustable bodywork", "energy deployment limitation"
MENTIONS = {
"B7.1.1": [DAB, "front wing profile", "rear wing flap", "fia standard ecu", "technical regulations", "driver", "fia", "competitor",
           "activation zone", "low grip activation zone", "circuit", "competition"],
"B7.1.2": ["driver", DAB, "fia standard ecu", "low grip conditions", "low grip activation zone"],
"B7.2.1": [EDL, "ers", "technical regulations", "f1 car", "competition", "fia", "competitor", "overtake", TT, LT, "control line", "detection gap",
           "detection line", "activation line", "low grip conditions", "sprint", "race", "boost mode", "fia-f1-doc-058", "fia-f1-doc-034", "championship", "circuit"],
"B7.2.2": ["overtake", LT, TT, "leader", "detection line", "safety car", "safety car period", "f1 car", "control line", "pit entry road", "pit lane",
           "low grip conditions", "race director"],
"B7.2.3": ["overtake", "driver", "fia standard ecu", LT, TT, "activation line", "detection line", "detection gap", "f1 car"],
"B7.2.4": ["overtake", "competitor", "race director", "driver", "detection gap", "detection line", "f1 car"],
}
add_fact("B7.1.1", DAB, "HAS_PART", "front wing profile", "rear wing flap", context="both controlled by the FIA Standard ECU")
add_fact("B7.1.1", DAB, "DEFINED_IN", "technical regulations", context="Articles C3.10.10 and C3.11.6; Corner Mode = deactivated, Straight Mode = activated")
add_fact("B7.1.1", DAB, "OCCURS_AT", "activation zone", context="full activation: front wing profiles and RW flap both in Straight Mode")
add_fact("B7.1.1", DAB, "OCCURS_AT", "low grip activation zone", context="partial activation: front wing profiles in Straight Mode, RW flap in Corner Mode")
add_fact("B7.1.1", "fia", "CONTROLS", "activation zone", "low grip activation zone", context="given to Competitors 4 weeks before; later changes need unanimous agreement, but the FIA may change them for safety")
add_fact("B7.1.2", DAB, "REQUIRES", "fia standard ecu", context="driver may activate it only when notified via the Control Electronics that it is enabled")
add_fact("B7.1.2", DAB, "APPLIES_DURING", "low grip conditions", context="only partial activation, in the Low Grip Activation Zones")
add_fact("B7.2.1", EDL, "DEFINED_IN", "technical regulations", context="ERS-K power limits in C5.2.8, Recharge limits in C5.2.10, power reduction in C5.12")
add_fact("B7.2.1", EDL, "DEFINED_IN", "fia-f1-doc-034", context="vehicle fundamentals used to justify changes")
add_fact("B7.2.1", "fia", "CONTROLS", EDL, context="per-Competition limits given 4 weeks before; provisional season document by 30 June; may be changed for safety at any time")
add_fact("B7.2.1", "fia", "CONTROLS", "detection gap", "detection line", "activation line", context="set per Competition with the energy limits")
add_fact("B7.2.1", EDL, "APPLIES_DURING", "championship", context="the C5.2.10ii Recharge limit applies at most 12 Competitions, of which at most four below 5 MJ")
add_fact("B7.2.1", EDL, "APPLIES_DURING", "low grip conditions", context="power reduction reset only in the last sector before the control line in an LTCS; never in a TTCS")
add_fact("B7.2.1", "boost mode", "APPLIES_DURING", "low grip conditions", context="allowed only to stop the power demand from being reduced, not to increase it")
add_fact("B7.2.1", "boost mode", "DEFINED_IN", "fia-f1-doc-058")
add_fact("B7.2.1", "overtake", "APPLIES_DURING", TT, context="extra Recharge on a lap when Overtake is enabled and activated at the control line")
add_fact("B7.2.2", "overtake", "APPLIES_DURING", LT, context="enabled before the start")
add_fact("B7.2.2", "overtake", "APPLIES_DURING", TT, context="disabled at the start or resumption; enabled once the leader first crosses the Detection Line")
add_fact("B7.2.2", "overtake", "APPLIES_DURING", "safety car period", context="disabled; re-enabled after all cars cross the control line once the safety car enters the pit entry road")
add_fact("B7.2.2", "overtake", "APPLIES_DURING", "low grip conditions", context="disabled")
add_fact("B7.2.2", "race director", "CONTROLS", "overtake", context="may disable or re-enable it for safety at their sole discretion")
add_fact("B7.2.3", "overtake", "REQUIRES", "fia standard ecu", context="driver may use it only when notified via the Control Electronics that it is enabled and activated")
add_fact("B7.2.3", "overtake", "APPLIES_DURING", LT, context="always activated when enabled")
add_fact("B7.2.3", "detection gap", "DETERMINES", "overtake", context="TTCS: within the gap of another car at the Detection Line means activated at the Activation Line; outside it means deactivated")
add_fact("B7.2.3", "overtake", "OCCURS_AT", "activation line")
add_fact("B7.2.3", "overtake", "OCCURS_AT", "detection line", context="gap to the car ahead is measured here")
add_fact("B7.2.4", "race director", "CONTROLS", "overtake", context="may allow manual operation if the notification system fails; the Competitor is then responsible for correct use")
build("B7", MENTIONS)
