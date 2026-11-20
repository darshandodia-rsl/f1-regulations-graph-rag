"""Entity/relationship extraction for Article B4 (Lap Time Classified Sessions (LTCS)). Writes data/extractions/B4.json."""

from common import *
VSC_EXC = "forbidden except: entering the pits after the first safety car line, leaving before the second safety car line, within the pit entry road/pit lane/pit exit road, or passing a car slowing with an obvious problem"
MENTIONS = {
"B4.1.1": ["driver", LT, "steward", "impeding", "unnecessary stop on track", "penalty", "circuit"],
"B4.1.2": [LT, "race director", "session interruption", "red flag", "marshal post", "start gantry", "control line", "f1 car", "pit lane",
           "fia standard ecu", "first safety car line", "marshalling sector", "fia light panel", "track", "q1", "q2", "q3", "sq1", "sq2", "sq3"],
"B4.1.3": ["race director", LT, "session interruption", "competition", "driver", TT],
"B4.1.4": ["virtual safety car", LT, "race director", "vsc deployed message", "vsc ending message", "fia light panel", "f1 car", "track",
           "pit entry road", "pit lane", "pit exit road", "fia standard ecu", "marshalling sector", "first safety car line", "second safety car line",
           "overtaking", "erratic driving", "minimum time breach", "driver"],
"B4.2.1": ["free practice", "session interruption", "fia", "commercial rights holder", SFC, AFC],
"B4.2.2": ["free practice", "driver", "practice start", "chequered flag", "control line", "starting grid", "f1 car", "race director", "red flag", "start gantry", "pit lane"],
"B4.3.1": ["sprint qualifying", "qualifying", "session interruption", "race director", "f1 car", "pit lane", "track"],
"B4.3.2": ["driver", "f1 car", "pit lane", "sprint qualifying", "qualifying"],
}
add_fact("B4.1.1", "impeding", "PUNISHABLE_BY", "penalty", context="during an LTCS, penalties under B1.9.4")
add_fact("B4.1.1", "unnecessary stop on track", "PUNISHABLE_BY", "penalty", context="during an LTCS, penalties under B1.9.4")
add_fact("B4.1.1", "impeding", "APPLIES_DURING", LT)
add_fact("B4.1.1", "unnecessary stop on track", "APPLIES_DURING", LT)
add_fact("B4.1.2", "race director", "CONTROLS", "session interruption", context="orders red flags at all marshal posts and the orange lights on the start gantry")
add_fact("B4.1.2", "red flag", "SIGNALS", "session interruption", context="all cars slow down and return to the pit lane, staying above the FIA ECU minimum time once in each marshalling sector")
add_fact("B4.1.2", "session interruption", "APPLIES_DURING", LT)
add_fact("B4.1.3", "race director", "CONTROLS", "session interruption", context="as often and as long as needed; no protest accepted about its effect on qualification")
add_fact("B4.1.4", "race director", "CONTROLS", "virtual safety car")
add_fact("B4.1.4", "virtual safety car", "APPLIES_DURING", LT, context="neutralises an LTCS")
add_fact("B4.1.4", "vsc deployed message", "SIGNALS", "virtual safety car", context="FIA light panels show VSC")
add_fact("B4.1.4", "fia light panel", "SIGNALS", "virtual safety car", context="show VSC while deployed; turn green 10-15 s after the VSC ENDING message")
add_fact("B4.1.4", "vsc ending message", "SIGNALS", "virtual safety car", context="ends it; panels turn green 10-15 s later")
add_fact("B4.1.4", "overtaking", "APPLIES_DURING", "virtual safety car", context=VSC_EXC)
add_fact("B4.1.4", "erratic driving", "APPLIES_DURING", "virtual safety car", context="on track, pit entry road or pit lane")
add_fact("B4.1.4", "minimum time breach", "APPLIES_DURING", "virtual safety car", context="must stay above the FIA ECU minimum time once in each marshalling sector and at both safety car lines")
add_fact("B4.2.1", "fia", "CONTROLS", "free practice", context="an interrupted free practice session may be extended if agreed between the FIA and the CRH")
add_fact("B4.2.1", "session interruption", "APPLIES_DURING", "free practice")
add_fact("B4.2.2", "practice start", "APPLIES_DURING", "free practice", context="after the end-of-session signal, for drivers still on track")
add_fact("B4.2.2", "practice start", "OCCURS_AT", "starting grid", context="complete one more lap, start from a marked grid position, never with a stationary car ahead on the same side")
add_fact("B4.2.2", "race director", "CONTROLS", "practice start", context="may stop practice starts with a red flag")
add_fact("B4.2.2", "red flag", "SIGNALS", "practice start", context="stops practice starts; cars return slowly to the pit lane")
add_fact("B4.3.1", "session interruption", "APPLIES_DURING", "sprint qualifying", "qualifying", context="the interrupted period is extended so its full running time is kept")
add_fact("B4.3.1", "race director", "CONTROLS", "session interruption", context="may end the period if no car could leave the pit lane and start a timed lap before its end")
build("B4", MENTIONS)
