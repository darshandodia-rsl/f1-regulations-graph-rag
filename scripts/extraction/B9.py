"""Entity/relationship extraction for Article B9 (Personnel Limitations). Writes data/extractions/B9.json."""

from common import *
RP, RP1, RP2, RP3 = "restricted period", "restricted period one", "restricted period two", "restricted period three"
MENTIONS = {
"B9.1.1": ["pass", "f1 car", "paddock", "pit lane", "track", "competition", "fia"],
"B9.2.1": ["competition", "fp1", "race", "competitor", "operational personnel", "f1 car", "circuit", "formation lap"],
"B9.2.2": ["driver", "non-operational personnel", "operational personnel", "competition"],
"B9.3.1": ["trainee personnel", "operational personnel", "competitor", "championship", "competition"],
"B9.4.1": ["personnel declaration", "fia", RP1, "document management system", "operational personnel", "trainee personnel", "competitor",
           "competition", "restricted area", "paddock", "designated garage area", "pit lane", "signalling area"],
"B9.5.1": [RP, "competition", "operational personnel", "trainee personnel", "circuit", RP1, RP2, RP3, "fp1", "fp2", "fp3", SFC, AFC,
           "formation lap", "sprint", "sprint qualifying"],
"B9.5.2": ["operational personnel", "trainee personnel", "paddock", RP, "circuit", RP1, RP2, RP3, "f1 car", "restricted period breach"],
"B9.5.3": ["competitor", "championship", RP, RP1, RP2, RP3, "competition", "restricted period breach", "driver", "race", "pit lane start"],
"B9.5.4": ["driver", "non-operational personnel", "competition", RP],
"B9.5.5": ["paddock", RP],
"B9.5.6": [RP1, "race director", "official supplier", "competition", "competitor"],
}
add_fact("B9.1.1", "fia", "CONTROLS", "pass", context="everyone in the paddock, pit lane or track must wear one; issued only with FIA agreement and used only by its holder")
add_fact("B9.2.1", "operational personnel", "APPLIES_DURING", "competition", context="max 60 per Competitor from 29 h before FP1 to 2 h after the Race start; unlimited from 45 min before the formation lap to 15 min after the Race start")
add_fact("B9.3.1", "trainee personnel", "APPLIES_DURING", "championship", context="16 individual exceptions per Competitor per Championship on top of the 60; each trainee max three Competitions")
add_fact("B9.4.1", "competitor", "REQUIRES", "personnel declaration", context="submitted before Restricted Period One; later changes at the FIA's discretion; exempt staff listed before the end of the Competition")
add_fact("B9.4.1", "personnel declaration", "REQUIRES", "document management system", context="uses the FIA's official template")
add_fact("B9.4.1", "restricted area", "HAS_PART", "paddock", "designated garage area", "pit lane", "signalling area")
add_fact("B9.5.1", RP, "APPLIES_DURING", "competition", context="operational and trainee personnel may not be within the circuit")
add_fact("B9.5.1", RP, "HAS_PART", RP1, context="42 h to 29 h before FP1")
add_fact("B9.5.1", RP, "HAS_PART", RP2, context="18 h to 4 h before FP1")
add_fact("B9.5.1", RP, "HAS_PART", RP3, context="SFC: 14 h to 3 h before FP3, starting earlier if the gap after FP2 exceeds 4 h")
add_fact("B9.5.1", RP, "HAS_PART", RP3, context="AFC: 14 h to 3 h before the Sprint formation lap, starting earlier if the gap after Sprint Qualifying exceeds 3 h")
add_fact("B9.5.1", RP3, "PRECEDES", "fp3", context="SFC")
add_fact("B9.5.1", RP3, "PRECEDES", "sprint", context="AFC")
add_fact("B9.5.2", "restricted period breach", "APPLIES_DURING", RP, context="staff may enter the paddock 30 min before a period ends and stay 1 h (RP1/RP2) or 30 min (RP3) after it starts for exercise, meals and socialising; any operational work then is a breach")
add_fact("B9.5.3", "restricted period breach", "PUNISHABLE_BY", "pit lane start", context="both drivers start the Race from the pit lane")
add_fact("B9.5.3", RP1, "APPLIES_DURING", "championship", context="six exceptions per Competitor per Championship, not used consecutively in one Competition")
add_fact("B9.5.3", RP2, "APPLIES_DURING", "championship", context="five exceptions per Competitor per Championship, not used consecutively in one Competition")
add_fact("B9.5.3", RP3, "APPLIES_DURING", "championship", context="four exceptions per Competitor per Championship, not used consecutively in one Competition")
add_fact("B9.5.4", "non-operational personnel", "APPLIES_DURING", RP, context="exempt; may load or unload freight, prepare equipment for other series and prepare garage displays")
add_fact("B9.5.5", RP, "OCCURS_AT", "paddock", context="warning boards placed before the turnstiles")
add_fact("B9.5.6", "race director", "CONTROLS", RP1, context="may grant all Competitors an extra exception (not counted) if an official supplier fails to deliver, no later than 12 h before it starts")
build("B9", MENTIONS)
