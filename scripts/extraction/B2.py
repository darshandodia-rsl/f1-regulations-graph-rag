"""Entity/relationship extraction for Article B2 (Format Of A Competition). Writes data/extractions/B2.json."""

from common import *
GRID = ["grid formation", "penalty", "steward", "drivers' championship classification", "driver", "grid place penalty",
        "unclassified driver", "starting grid", "competitor", "f1 car", "formation lap"]
MENTIONS = {
"B2.1.1": [SFC, "free practice", "fp1", "fp2", "fp3", "in-competition tyre testing", "tyre"],
"B2.1.2": [AFC, "free practice", "fp1"],
"B2.1.3": ["free practice classification", "free practice", "driver", "control line", "pit lane"],
"B2.2.1": [AFC, "sprint", "starting grid", "sprint qualifying", "fp1"],
"B2.2.2": ["sprint qualifying", "sq1", "sq2", "sq3", "f1 car", "track"],
"B2.2.3": ["sprint qualifying classification", "sprint qualifying", "sq1", "sq2", "sq3", "driver", "unclassified driver", "race director",
           "wet track declaration", "steward", "disqualification", "fp1", "control line", "f1 car", "competition", "championship"],
"B2.3.1": [AFC, "sprint"],
"B2.3.2": ["sprint", "start signal", "chequered flag", "formation lap behind safety car", "safety car"],
"B2.3.3": ["sprint", "chequered flag", "leader", "control line", "suspension"],
"B2.3.4": GRID + ["sprint", "sprint qualifying", "sprint qualifying classification"],
"B2.3.5": ["sprint classification", "sprint", "f1 car", "control line", ISC, REGS],
"B2.4.1": ["qualifying", "race", "starting grid", SFC, AFC, "fp3", "sprint"],
"B2.4.2": ["qualifying", "q1", "q2", "q3", "f1 car", "track"],
"B2.4.3": ["qualifying classification", "qualifying", "q1", "q2", "q3", "driver", "unclassified driver", "race director",
           "wet track declaration", "steward", "disqualification", LT, "control line", "f1 car", "competition", "championship"],
"B2.5.1": ["race", "competition"],
"B2.5.2": ["race", "start signal", "chequered flag", "formation lap behind safety car", "safety car", "monaco"],
"B2.5.3": ["race", "chequered flag", "leader", "control line", "suspension"],
"B2.5.4": GRID + ["race", "qualifying", "qualifying classification"],
"B2.5.5": ["race classification", "race", "f1 car", "control line", ISC, REGS],
}
add_fact("B2.1.1", SFC, "HAS_PART", "fp1", "fp3", context="1 h each")
add_fact("B2.1.1", SFC, "HAS_PART", "fp2", context="1 h, or 1.5 h if extra ICTT tyre specifications are provided")
for f in ["fp1", "fp2", "fp3"]:
    add_fact("B2.1.1", f, "TYPE_OF", "free practice")
add_fact("B2.1.1", "fp1", "PRECEDES", "fp2", context="same day, separated by 2 to 3 h")
add_fact("B2.1.1", "fp2", "PRECEDES", "fp3", context="FP3 starts at least 18 h after FP2 ends (17.5 h with ICTT)")
add_fact("B2.1.2", AFC, "HAS_PART", "fp1", context="the only free practice session; 1 h on the first day")
add_fact("B2.1.2", "fp1", "TYPE_OF", "free practice")
add_fact("B2.1.3", "free practice", "DETERMINES", "free practice classification", context="fastest lap; ties go to whoever set the time first; laps must start and finish at the control line on track, not in the pit lane")
add_fact("B2.2.1", AFC, "HAS_PART", "sprint qualifying")
add_fact("B2.2.1", "sprint qualifying", "DETERMINES", "sprint", context="sets the Sprint starting grid")
add_fact("B2.2.1", "fp1", "PRECEDES", "sprint qualifying", context="SQ starts 2.5 to 3.5 h after FP1 ends, first day")
add_fact("B2.2.2", "sprint qualifying", "HAS_PART", "sq1", context="12 min; slowest six eliminated")
add_fact("B2.2.2", "sprint qualifying", "HAS_PART", "sq2", context="10 min; slowest six eliminated")
add_fact("B2.2.2", "sprint qualifying", "HAS_PART", "sq3", context="8 min; remaining ten cars")
add_fact("B2.2.2", "sq1", "PRECEDES", "sq2", context="7 min break")
add_fact("B2.2.2", "sq2", "PRECEDES", "sq3", context="7 min break")
add_fact("B2.2.3", "sprint qualifying", "DETERMINES", "sprint qualifying classification", context="positions 1-10 from SQ3, 11-16 from SQ2, 17-22 from SQ1 (based on 22 cars)")
add_fact("B2.2.3", "fp1", "DETERMINES", "sprint qualifying classification", context="orders the unclassified drivers")
add_fact("B2.2.3", "steward", "CONTROLS", "unclassified driver", context="decide whether unclassified drivers take further part in the Competition")
add_fact("B2.2.3", "race director", "CONTROLS", "wet track declaration")
add_fact("B2.2.3", "wet track declaration", "APPLIES_DURING", "sq1", context="the 107% rule does not apply if the track is declared wet")
add_fact("B2.3.1", AFC, "HAS_PART", "sprint", context="second day of track running")
add_fact("B2.3.2", "start signal", "SIGNALS", "sprint")
add_fact("B2.3.2", "chequered flag", "SIGNALS", "sprint", context="distance: fewest complete laps exceeding 100 km")
add_fact("B2.3.2", "formation lap behind safety car", "APPLIES_DURING", "sprint", context="Sprint laps reduced by the safety car laps minus one")
add_fact("B2.3.3", "chequered flag", "SIGNALS", "sprint", context="shown to the leader at the end of the lap after one hour has elapsed")
add_fact("B2.3.3", "suspension", "APPLIES_DURING", "sprint", context="suspension time is added to the 1 h limit, up to 1.5 h in total")
add_fact("B2.3.4", "sprint qualifying classification", "DETERMINES", "grid formation", context="Sprint grid; classified drivers' grid penalties are added to their position")
add_fact("B2.3.4", "drivers' championship classification", "DETERMINES", "grid formation", context="Sprint grid if Sprint Qualifying cannot take place")
add_fact("B2.3.4", "steward", "CONTROLS", "grid formation", context="Sprint grid at their sole discretion if neither method can be applied")
add_fact("B2.3.4", "grid place penalty", "APPLIES_DURING", "grid formation", context="Sprint: more than 15 cumulative places means starting behind all classified drivers")
add_fact("B2.3.4", "grid formation", "APPLIES_DURING", "sprint", context="provisional grid at least 2 h before the formation lap, final grid 1 h before; non-starters must tell the stewards 1¼ h before")
add_fact("B2.3.5", "sprint", "DETERMINES", "sprint classification", context="most laps, then order across the control line; cars under 90% of the winner's laps are not classified")
add_fact("B2.4.1", "qualifying", "DETERMINES", "race", context="sets the Race starting grid")
add_fact("B2.4.1", SFC, "HAS_PART", "qualifying")
add_fact("B2.4.1", AFC, "HAS_PART", "qualifying")
add_fact("B2.4.1", "fp3", "PRECEDES", "qualifying", context="SFC: qualifying starts 2 to 3 h after FP3, second day")
add_fact("B2.4.1", "sprint", "PRECEDES", "qualifying", context="AFC: qualifying starts 3 to 4 h after the Sprint, second day")
add_fact("B2.4.2", "qualifying", "HAS_PART", "q1", context="18 min; slowest six eliminated")
add_fact("B2.4.2", "qualifying", "HAS_PART", "q2", context="15 min; slowest six eliminated")
add_fact("B2.4.2", "qualifying", "HAS_PART", "q3", context="13 min; remaining ten cars")
add_fact("B2.4.2", "q1", "PRECEDES", "q2", context="7 min break")
add_fact("B2.4.2", "q2", "PRECEDES", "q3", context="7 min break")
add_fact("B2.4.3", "qualifying", "DETERMINES", "qualifying classification", context="positions 1-10 from Q3, 11-16 from Q2, 17-22 from Q1 (based on 22 cars)")
add_fact("B2.4.3", LT, "DETERMINES", "qualifying classification", context="unclassified drivers are ordered by the last LTCS they all took part in")
add_fact("B2.4.3", "steward", "CONTROLS", "unclassified driver", context="decide whether unclassified drivers take further part in the Competition")
add_fact("B2.4.3", "race director", "CONTROLS", "wet track declaration")
add_fact("B2.4.3", "wet track declaration", "APPLIES_DURING", "q1", context="the 107% rule does not apply if the track is declared wet")
add_fact("B2.5.1", "competition", "HAS_PART", "race", context="third day of track running at all Competitions")
add_fact("B2.5.2", "start signal", "SIGNALS", "race")
add_fact("B2.5.2", "chequered flag", "SIGNALS", "race", context="distance: fewest complete laps exceeding 305 km")
add_fact("B2.5.2", "formation lap behind safety car", "APPLIES_DURING", "race", context="Race laps reduced by the safety car laps minus one")
add_fact("B2.5.2", "race", "OCCURS_AT", "monaco", context="Monaco race distance is 260 km")
add_fact("B2.5.3", "chequered flag", "SIGNALS", "race", context="shown to the leader at the end of the lap after two hours have elapsed")
add_fact("B2.5.3", "suspension", "APPLIES_DURING", "race", context="suspension time is added to the 2 h limit, up to 3 h in total")
add_fact("B2.5.4", "qualifying classification", "DETERMINES", "grid formation", context="Race grid; classified drivers' grid penalties are added to their position")
add_fact("B2.5.4", "drivers' championship classification", "DETERMINES", "grid formation", context="Race grid if Qualifying cannot take place")
add_fact("B2.5.4", "steward", "CONTROLS", "grid formation", context="Race grid at their sole discretion if neither method can be applied")
add_fact("B2.5.4", "grid place penalty", "APPLIES_DURING", "grid formation", context="Race: more than 15 cumulative places means starting behind all classified drivers")
add_fact("B2.5.4", "grid formation", "APPLIES_DURING", "race", context="provisional grid at least 2 h before the formation lap, final grid 1 h before; non-starters must tell the stewards 1¼ h before")
add_fact("B2.5.5", "race", "DETERMINES", "race classification", context="most laps, then order across the control line; cars under 90% of the winner's laps are not classified")
build("B2", MENTIONS)
