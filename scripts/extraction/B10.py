"""Entity/relationship extraction for Article B10 (Media Activities & Official Ceremonies). Writes data/extractions/B10.json."""

from common import *
MA, FAN, PC, MD = "media activity", "fan engagement activity", "press conference", "media delegate"
SCR = "senior competitor representative"
MENTIONS = {
"B10.1.1": ["driver", MA, MD, "fp1", PC, "competitor", FAN, "commercial rights holder", "testing of current car", "competition",
            "document management system", "fia", "media", "pre-event car display"],
"B10.1.2": ["competitor", "f1 car", "designated garage area", "pre-event car display", "fp1", "pit lane", MD, "media", "pit stop", "technical delegate",
            "power unit manufacturer", MA, "competition", "championship", FAN, "commercial rights holder", "driver", SFC, "fp2", SCR, AFC,
            "sprint qualifying", PC, "team principal", "team ceo", "technical director", "additional driver", "testing of current car"],
"B10.1.3": ["fp3", "formation lap", "sprint", "competition", "driver", MD, "commercial rights holder", FAN, "q1", "q2", "q3", "weighing", MA, PC,
            "qualifying", "media delegate's note", AFC, "media centre"],
"B10.1.4": ["driver", "drivers parade", "formation lap", "competitor", MD, "media delegate's note", "race", "starting grid", MA, "weighing", SCR, "media"],
"B10.2.1": ["driver", "race", "podium ceremony", "podium", MA, PC, "media centre", "monaco"],
"B10.2.2": ["podium ceremony", "driver", "race", "flame-resistant clothing", MA],
"B10.2.3": [MA, PC, "driver"],
"B10.2.4": ["podium ceremony", MA],
}
add_fact("B10.1.1", MD, "CONTROLS", MA, context="day before running: up to six drivers for max 1 h in a 2 h window from 23 h before FP1; other drivers do team-run sessions")
add_fact("B10.1.1", MD, "CONTROLS", PC, context="designates the official FIA Press Conference")
add_fact("B10.1.1", FAN, "PRECEDES", "fp1", context="day before running: six drivers, 30 min each in a 1 h window from 20.5 h before FP1")
add_fact("B10.1.1", "competitor", "REPORTS_TO", MD, context="summary of new aero and bodywork parts no later than 23 h before FP1; released via the DMS 1 h before the car display")
add_fact("B10.1.2", "pre-event car display", "PRECEDES", "fp1", context="both cars outside the garage for up to 1 h, starting no later than 1.5 h before FP1, fitted with the parts to be used in FP1")
add_fact("B10.1.2", MD, "CONTROLS", "pre-event car display", context="decides where the cars are positioned; media may film and photograph")
add_fact("B10.1.2", "technical delegate", "CONTROLS", "pre-event car display", context="approves exceptions in writing")
add_fact("B10.1.2", "power unit manufacturer", "REQUIRES", MA, context="one media presentation of at least 30 min per Championship, notified 4 weeks ahead")
add_fact("B10.1.2", MD, "CONTROLS", FAN, context="first day: up to 12 drivers chosen with the CRH, 30 min each, ending 1.5 h before FP1")
add_fact("B10.1.2", SCR, "REQUIRES", MA, context="SFC: one driver and one senior representative available after FP2; up to six team representatives 1 h after FP1")
add_fact("B10.1.2", "driver", "REQUIRES", MA, context="AFC: available right after their Sprint Qualifying elimination; no top-three press conference after SQ")
for t in ["team principal", "team ceo", "technical director"]:
    add_fact("B10.1.2", t, "TYPE_OF", SCR, context="each Competitor needs at least four senior representatives for media activities, including these")
add_fact("B10.1.2", "team principal", "REQUIRES", FAN, context="three Team Principals not in the media activities, chosen with the CRH")
add_fact("B10.1.3", MD, "CONTROLS", FAN, context="second day: up to 12 drivers who didn't do it on day one, ending 1.5 h before FP3 or the Sprint formation lap")
add_fact("B10.1.3", "driver", "REQUIRES", MA, context="drivers eliminated in Q1/Q2, and Q3 drivers not in the press conference, right after being weighed")
add_fact("B10.1.3", "weighing", "PRECEDES", MA)
add_fact("B10.1.3", "driver", "REQUIRES", PC, context="top three in Qualifying (post-qualifying procedures); AFC: top three in the Sprint, 15 min in the media centre then 15 min TV")
add_fact("B10.1.3", PC, "DEFINED_IN", "media delegate's note", context="post-qualifying procedures")
add_fact("B10.1.4", "driver", "REQUIRES", "drivers parade", context="all drivers, 30 min starting 2 h before the formation lap; at the front of the grid 16 min before for the national anthem")
add_fact("B10.1.4", MD, "CONTROLS", "drivers parade")
add_fact("B10.1.4", "drivers parade", "PRECEDES", "race")
add_fact("B10.1.4", "race", "DEFINED_IN", "media delegate's note", context="pre-race and post-race procedures")
add_fact("B10.1.4", "driver", "REQUIRES", MA, context="Race retirees after returning to the paddock; finishers outside the top three after being weighed")
add_fact("B10.1.4", SCR, "REQUIRES", MA, context="one senior spokesperson for TV during the Race, and one at hospitality for 5 min, 1-2 h after the Race")
add_fact("B10.2.1", "driver", "REQUIRES", "podium ceremony", context="top three plus a winning constructor representative; then 1.5 h for TV and the press conference")
add_fact("B10.2.1", "podium ceremony", "OCCURS_AT", "podium", context="procedure in Appendix B4, except at Monaco")
add_fact("B10.2.1", PC, "OCCURS_AT", "media centre")
add_fact("B10.2.2", "driver", "REQUIRES", "flame-resistant clothing", context="top three keep driving suits done up to the neck through the podium and interviews")
add_fact("B10.2.4", MA, "APPLIES_DURING", "podium ceremony", context="if no points are awarded there is no podium, but TV interviews still happen at that time")
build("B10", MENTIONS)
