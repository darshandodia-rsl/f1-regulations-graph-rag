"""Entity/relationship extraction for Article B5 (Total Time Classified Sessions (TTCS)). Writes data/extractions/B5.json."""

from common import *
PEN4 = [S5, S10, DT, SG]
SIG5 = ["ten minute signal", "five minute signal", "three minute signal", "one minute signal", "fifteen second signal"]
VSC_EXC = "forbidden except: entering the pits after the first safety car line, leaving before the second safety car line, within the pit entry road/pit lane/pit exit road, or passing a car slowing with an obvious problem"
SUSP = ["red flag", "marshal post", "control line", "start gantry", "f1 car", "pit lane", "race director", "fast lane", "pit entry road", "starting grid", "pole position", "competitor", "resumption procedure"]
RESUME = ["race director", "competitor", "fia light panel", "pit lane exit", "safety car orange lights", "safety car", "pit lane", "leader", "f1 car",
          "designated garage area", "fast lane", "starting procedure suspension", "resumption procedure suspension", "inner lane",
          "formation lap behind safety car", SG, TT, "driver"]
MENTIONS = {
"B5.1.1": ["driver", TT, LT],
"B5.1.2": ["starting grid"],
"B5.1.3": ["f1 car", "starting grid"],
"B5.1.4": ["refuelling", "f1 car", "pit lane", "reconnaissance lap", "chequered flag"],
"B5.1.5": ["suspension", TT, "tyre blanket", "pit lane", "designated pit stop position"],
"B5.1.6": ["driver", "f1 car", "pit lane", TT, "disqualification", "suspension"],
"B5.1.7": ["safety car", "fia", "safety car driver", "safety car observer", "f1 car", "race control"],
"B5.1.8": ["race director", TT, "pit wall", "team personnel", "official", "fire marshal"],
"B5.2.1": ["pit lane", "reconnaissance lap", "safety car", "starting grid", "five minute signal", "track"],
"B5.2.2": ["formation lap", TT, "pit lane exit", "f1 car", "pit lane", "reconnaissance lap", "driver", "sprint", "race", "pit entry road",
           "designated garage area", "designated pit stop position", "track"],
"B5.2.3": ["f1 car", TT, "starting grid", "pit lane", "internal combustion engine", "pit lane starter"],
"B5.2.4": ["f1 car", "reconnaissance lap", "starting grid", TT],
"B5.2.5": ["f1 car", "pit lane", "pit lane exit", "reconnaissance lap", TT],
"B5.3.1": ["reconnaissance lap", "driver", TT, "pit lane", "f1 car", "designated garage area", "pit lane exit", "formation lap", "fast lane", "pit lane starter"],
"B5.3.2": ["f1 car", TT, "pit lane", "grid formation", "sprint", "race", "pit lane exit", "five minute signal", "pit lane starter"],
"B5.3.3": ["fast lane", "formation lap", "team personnel", "internal combustion engine", "tyre", "front wing profile", "fia standard ecu", "marshal", "technical regulations", "pit lane starter", "driver"],
"B5.4.1": ["grid procedure", "race director", TT, "delayed start", "formation lap", "start gantry", "delayed start message", "competitor"],
"B5.4.2": ["start procedure", "ten minute signal", "delayed start"],
"B5.5.1": [TT, "formation lap", "grid procedure"] + SIG5,
"B5.5.2": ["ten minute signal", "driver", "official", "team personnel", "starting grid", TT, "formation lap behind safety car", "safety car",
           "safety car orange lights", "competitor", "official messaging system", "wet-weather tyre"],
"B5.5.3": ["five minute signal", "f1 car", "starting grid", "fast lane", "inner lane", "wheels not fitted at five minute signal", SG,
           "tyre blanket", "delayed start", "aborted start", "team personnel", "driver"],
"B5.5.4": ["three minute signal", "team personnel", "competitor", "starting grid"],
"B5.5.5": ["one minute signal", "internal combustion engine", "team personnel", "starting grid", "fast lane", "fifteen second signal", "f1 car",
           "pit lane start", SG, DT, "personnel on grid after fifteen second signal", "driver", "marshal", "inner lane", "waved yellow flag", TT, "pit lane"],
"B5.5.6": ["f1 car", "starting grid", "inner lane", "designated garage area", "formation lap", TT, "pit lane start", "pit lane"],
"B5.6.1": ["start gantry", "f1 car", "starting grid", "formation lap", "pole position", "pit lane", "pit lane exit", "pit lane starter"],
"B5.6.2": ["driver", "starting grid", "pole position", "pit lane"],
"B5.6.3": ["formation lap", "practice start"],
"B5.6.4": ["overtaking", "formation lap", "f1 car", "driver", "first safety car line", "pit lane", TT, SG, "pit lane start"],
"B5.7.1": ["formation lap", TT, "f1 car", "starting grid", "driver", "marshal", "waved yellow flag", "grid light panel", "race director",
           "inner lane", "fast lane", "aborted start", "extra formation lap", "start procedure"],
"B5.7.2": ["f1 car", "starting grid", "formation lap", "standing start", "start lights", "permanent starter", "grid light panel", "start gantry", "start signal", TT],
"B5.7.3": ["pit lane starter", "pit lane", "formation lap", "pit lane exit", "fast lane", TT, "track"],
"B5.8.1": ["formation lap", TT, "race director", "aborted start", "start gantry", "aborted start message", "starting grid", "fast lane",
           "team personnel", "official messaging system", "competitor", "ten minute signal", "grid procedure"],
"B5.8.2": ["driver", "aborted start", TT, "pit lane start", "pit lane", SG],
"B5.8.3": ["aborted start", TT],
"B5.9.1": ["formation lap", TT, "aborted start", "race director", "extra formation lap", "start gantry", "extra formation lap message",
           "starting grid", "competitor", "pole position", "pit lane", "pit lane exit", "pit lane starter"],
"B5.9.2": ["extra formation lap", "f1 car", "starting grid", "pit lane", "team personnel", "pit lane exit"],
"B5.9.3": ["race director", "extra formation lap", "aborted start"],
"B5.9.4": ["driver", "extra formation lap", "pit lane", "pit lane start", TT, SG],
"B5.9.5": ["extra formation lap", TT],
"B5.9.6": ["extra formation lap", TT, "championship"],
"B5.10.1": [TT, "formation lap behind safety car", "safety car", "race director", "wet-weather tyre", "ten minute signal", "five minute signal",
            "safety car orange lights", "formation lap behind safety car message", "competitor", "driver"],
"B5.10.2": ["start gantry", "safety car", "starting grid", "driver", "race director", "low visibility message", "leader", "f1 car"],
"B5.10.3": ["driver", "starting grid", "pole position", "pit lane"],
"B5.10.4": ["f1 car", TT, "pit lane", "formation lap behind safety car", "safety car", "pit lane starter"],
"B5.10.5": ["pit lane", "safety car", "formation lap behind safety car", "f1 car", "track", TT, "pit lane start"],
"B5.10.6": ["overtaking", "formation lap behind safety car", "f1 car", "starting grid", "pit lane", "safety car", "standing start", "rolling start",
            "first safety car line", TT, SG, "rolling start message", "competitor", "driver"],
"B5.10.7": ["formation lap behind safety car", "safety car", TT, "sprint", "race"],
"B5.10.8": ["standing start", "safety car", "formation lap behind safety car", TT, "standing start message", "competitor", "fia light panel",
            "pit lane exit", "safety car orange lights", "driver", "pit lane", "f1 car", "starting grid", "start procedure", "leader", "pit lane start",
            SG, "race director", "extra formation lap", "starting procedure suspension"],
"B5.10.9": ["rolling start", "safety car", "formation lap behind safety car", TT, "rolling start message", "competitor", "fia light panel",
            "pit lane exit", "safety car orange lights", "driver", "pit entry road", "f1 car", "green flag", "control line", "overtaking", "pit lane", SG, "leader"],
"B5.11.1": ["standing start", "standing start resumption", "start lights", "starting grid", "transponder", "tyre", "start signal", "steward",
            "driver", "false start", "f1 car"] + PEN4,
"B5.12": ["virtual safety car", "double waved yellow flag", "track", "competitor", "official", "safety car"],
"B5.12.1": ["virtual safety car", TT, "race director", "vsc deployed message", "competitor", "fia light panel"],
"B5.12.2": ["virtual safety car", "f1 car", "erratic driving", "track", "pit entry road", "pit lane", "fia standard ecu", "marshalling sector",
            "first safety car line", "second safety car line", "fia light panel", TT, "steward", "minimum time breach", "overtaking", "pit exit road", "driver"] + PEN4,
"B5.12.3": [TT, "virtual safety car", "pit stop", "f1 car", "tyre"],
"B5.12.4": ["race director", "virtual safety car", "vsc ending message", "competitor", "fia light panel", "driver"],
"B5.12.5": ["virtual safety car", TT],
"B5.13": ["safety car", "safety car period", "competitor", "official", "track", TT, "suspension"],
"B5.13.1": ["safety car", "safety car period", TT, "race director", "safety car deployed message", "competitor", "fia light panel", "marshal post",
            "waved yellow flag", "sc board", "safety car orange lights", "track", "leader"],
"B5.13.2": ["safety car period", "f1 car", "erratic driving", "track", "pit entry road", "pit lane", "safety car", "safety car deployed message",
            "competitor", "first safety car line", "second safety car line", "fia standard ecu", "marshalling sector", "fia light panel", "steward",
            "minimum time breach", "race director", "low visibility message", "overtaking", "control line", "safety car green light", "pit exit road",
            "designated garage area", "leader", "driver"] + PEN4,
"B5.13.3": ["race director", "safety car", "safety car period", "f1 car", "pit lane", "pit entry road", "official messaging system", "competitor",
            "track", "pit exit road", "overtaking", "designated garage area", DT, "driver", "pit stop", "tyre"],
"B5.13.4": ["race director", "safety car green light", "safety car", "f1 car", "leader", "overtaking", "overtaking will not be permitted message",
            "lapped cars may now overtake message", "lapped car", "competitor", "control line", "first safety car line", "pit lane exit", "safety car period"],
"B5.13.5": ["safety car", "leader", "f1 car", "lapped cars may now overtake message", "competitor", "race director", "safety car period"],
"B5.13.6": ["race director", "safety car period", "safety car in this lap message", "competitor", "safety car orange lights", "safety car", "pit lane",
            "leader", "f1 car", "pit entry road", "driver", "sc board", "waved yellow flag", "green flag", "control line", TT],
"B5.13.7": ["safety car", TT, "formation lap behind safety car", "safety car period"],
"B5.13.8": ["safety car", "race director", "chequered flag", "f1 car", "control line", "overtaking", "sc board", "waved yellow flag",
            "safety car orange lights", "pit entry road", "pit lane", "parc fermé", "competitor", "driver", "safety car period"],
"B5.14.1": SUSP + ["starting procedure suspension", "formation lap behind safety car", TT, "starting procedure suspended message", "safety car", "pit lane exit"],
"B5.14.2": SUSP + ["suspension", TT, "overtaking", "pit lane exit", "sprint", "race"],
"B5.14.3": SUSP + ["resumption procedure suspension", "safety car", "resumption procedure suspended message", "pit lane exit"],
"B5.14.4": ["starting procedure suspension", "suspension", "resumption procedure suspension", "resumption procedure", "f1 car", "fast lane",
            "internal combustion engine", "tyre", "driver cooling system", "heat hazard", "front wing profile", "fia standard ecu", "technical regulations",
            "team personnel", "official", "media", "fia", "pit lane"],
"B5.15.1": ["resumption order", "resumption procedure", "fast lane", "starting procedure suspension", "f1 car", "pit lane", "safety car", "pit lane start",
            "formation lap behind safety car", "suspension", "track", "pit entry road", "resumption procedure suspension", "designated garage area",
            "competitor", "ten minute signal"],
"B5.15.2": ["resumption procedure", "competitor", "official messaging system", "race director", "wet-weather tyre", "safety car orange lights",
            "safety car lights on message", "safety car", "f1 car", "fast lane", "tyre blanket", "delayed start", "wheels not fitted at five minute signal",
            SG, "suspension", "leader", "lapped car", "pit lane", "team personnel", "personnel on grid after fifteen second signal", "pit lane exit",
            "pit lane start", "standing start resumption", "rolling start resumption", "low visibility message", "starting procedure suspension",
            "resumption procedure suspension", "marshal", "inner lane", "waved yellow flag", TT, "track", "driver"] + SIG5,
"B5.15.3": ["overtaking", "safety car", "f1 car", "fast lane", "pit lane", "resumption order", "standing start resumption", "rolling start resumption",
            "first safety car line", "pit lane exit", SG, DT, "rolling start message", "competitor", "steward", "unauthorised overtaking", TT, "driver"],
"B5.15.4": RESUME + ["standing start resumption", "standing start message", "starting grid", "resumption order", "start procedure", "extra formation lap"],
"B5.15.5": RESUME + ["rolling start resumption", "rolling start message", "pit entry road", "green flag", "control line", "overtaking"],
"B5.16.1": ["chequered flag", "sprint", "race", "control line", "leader", "f1 car", "track", "pit lane", "race director", "safety car", "finishing procedure"],
"B5.16.2": ["chequered flag", "leader", TT, "control line"],
"B5.16.3": ["chequered flag", "f1 car", "circuit", "parc fermé", "marshal", "driver", "race", "podium ceremony", "official"],
}
add_fact("B5.1.1", LT, "PRECEDES", TT, context="a driver must take part in at least one LTCS to start a TTCS")
add_fact("B5.1.4", "refuelling", "APPLIES_DURING", "reconnaissance lap", context="forbidden from leaving for the reconnaissance laps until the end-of-session signal")
add_fact("B5.1.5", "tyre blanket", "APPLIES_DURING", TT, context="not permitted in the pit lane during a TTCS except during a suspension")
add_fact("B5.1.6", "disqualification", "APPLIES_DURING", TT, context="car that stops outside the pit lane and rejoins after physical assistance")
add_fact("B5.1.7", "fia", "APPOINTS", "safety car driver")
add_fact("B5.1.7", "safety car driver", "CONTROLS", "safety car")
add_fact("B5.1.7", "safety car observer", "REPORTS_TO", "safety car driver", context="rides in the safety car, recognises all cars, in permanent radio contact with race control")
add_fact("B5.1.8", "race director", "CONTROLS", "pit wall", context="kept clear at the start except the 12 permitted team members, officials and fire marshals")
add_fact("B5.2.1", "safety car", "OCCURS_AT", "starting grid", context="takes position at the front of the grid before the pit lane opens; laps the track at the five minute signal")
add_fact("B5.2.2", "reconnaissance lap", "PRECEDES", "formation lap")
add_fact("B5.2.2", "reconnaissance lap", "APPLIES_DURING", "sprint", context="pit lane exit opens 30 min before the formation lap for 5 min; one lap each")
add_fact("B5.2.2", "reconnaissance lap", "APPLIES_DURING", "race", context="pit lane exit opens 40 min before the formation lap for 10 min; extra laps via the pit lane at greatly reduced speed")
add_fact("B5.2.4", "reconnaissance lap", "PRECEDES", TT, context="a car that doesn't complete one and reach the grid under its own power may not start from the grid")
add_fact("B5.2.5", "reconnaissance lap", "PRECEDES", TT, context="a car still in the pit lane when the exit closes may start from the end of the pit lane")
add_fact("B5.3.1", "pit lane starter", "TYPE_OF", "driver", context="leaves the garage only after the pit lane exit closes before the formation lap; waits in line in the fast lane")
add_fact("B5.3.2", "grid formation", "DETERMINES", "pit lane starter", context="order of pit lane starters; cars reaching the pit exit after the five minute signal go behind")
add_fact("B5.3.3", "pit lane starter", "TYPE_OF", "driver", context="limited work in the fast lane until 15 s before the formation lap: engine start, cooling/heating devices, driver comfort, wheels and tyres, front wing profiles")
add_fact("B5.3.3", "front wing profile", "DEFINED_IN", "technical regulations", context="Article C3.10.10")
add_fact("B5.4.1", "race director", "CONTROLS", "delayed start", context="during the grid procedure, before the formation lap")
add_fact("B5.4.1", "delayed start message", "SIGNALS", "delayed start", context="orange lights on the start gantry and a DELAYED START board")
add_fact("B5.4.2", "delayed start", "PRECEDES", "start procedure", context="the starting procedure restarts at the ten minute signal")
for g in SIG5:
    add_fact("B5.5.1", g, "SIGNALS", "grid procedure", context="countdown to the formation lap, each with an audible warning")
add_fact("B5.5.2", "safety car orange lights", "SIGNALS", "formation lap behind safety car", context="lit at the ten minute signal; Competitors told via the OMS")
add_fact("B5.5.2", "formation lap behind safety car", "REQUIRES", "wet-weather tyre", context="compulsory when announced at the ten minute signal")
add_fact("B5.5.3", "wheels not fitted at five minute signal", "PUNISHABLE_BY", SG)
add_fact("B5.5.3", "wheels not fitted at five minute signal", "OCCURS_AT", "starting grid", "fast lane", context="after this signal wheels may only be removed in the inner lane")
add_fact("B5.5.3", "tyre blanket", "APPLIES_DURING", "delayed start", "aborted start", context="disconnected at the five minute signal; may be reconnected only after a delayed or aborted start")
add_fact("B5.5.5", "personnel on grid after fifteen second signal", "PUNISHABLE_BY", "pit lane start", context="car on the grid")
add_fact("B5.5.5", "personnel on grid after fifteen second signal", "PUNISHABLE_BY", SG, context="if that driver then fails to start from the pit lane")
add_fact("B5.5.5", "personnel on grid after fifteen second signal", "PUNISHABLE_BY", DT, context="car in the pit lane fast lane")
add_fact("B5.5.5", "marshal", "CONTROLS", "f1 car", context="pushes a car whose driver raised their hands into the inner lane once the field has left; yellow flags shown beside it")
add_fact("B5.5.6", "pit lane start", "APPLIES_DURING", TT, context="car moved from the grid to the inner lane or garage before the formation lap")
add_fact("B5.6.1", "start gantry", "SIGNALS", "formation lap", context="green lights; pole position driver leads; pit lane starters join after the field passes the pit exit")
add_fact("B5.6.3", "practice start", "APPLIES_DURING", "formation lap", context="forbidden; formation kept as tight as possible")
add_fact("B5.6.4", "overtaking", "APPLIES_DURING", "formation lap", context="only to restore the starting order after a car is delayed")
add_fact("B5.6.4", "pit lane start", "APPLIES_DURING", "formation lap", context="delayed driver who hasn't restored their position by the first safety car line")
add_fact("B5.6.4", SG, "APPLIES_DURING", "formation lap", context="delayed driver who hasn't restored position and fails to enter the pit lane")
add_fact("B5.7.1", "waved yellow flag", "SIGNALS", "start procedure", context="marshals wave them when a car is immobilised on the grid")
add_fact("B5.7.1", "grid light panel", "SIGNALS", "start procedure", context="yellow when a car is immobilised on the grid")
add_fact("B5.7.1", "marshal", "CONTROLS", "f1 car", context="pushes an immobilised car into the inner lane when the race director deems it safe; it may join once the TTCS has started")
add_fact("B5.7.1", "race director", "CONTROLS", "aborted start", "extra formation lap")
add_fact("B5.7.2", "permanent starter", "CONTROLS", "start lights", context="five red lights 1 s apart; time to lights out at their sole discretion")
add_fact("B5.7.2", "start signal", "SIGNALS", TT, context="all red lights extinguished")
add_fact("B5.7.2", "grid light panel", "SIGNALS", "standing start", context="flashing blue for 5 s and Pre-Start on the gantry once all cars have stopped")
add_fact("B5.7.2", "standing start", "APPLIES_DURING", TT, context="cars stop in their grid positions with engines running")
add_fact("B5.8.1", "race director", "CONTROLS", "aborted start")
add_fact("B5.8.1", "aborted start message", "SIGNALS", "aborted start", context="orange lights on the start gantry and an ABORTED START board")
add_fact("B5.8.1", "aborted start", "PRECEDES", "grid procedure", context="restarts at the ten minute signal; Competitors informed via the OMS")
add_fact("B5.8.2", "pit lane start", "APPLIES_DURING", "aborted start", context="the driver who caused it")
add_fact("B5.8.2", SG, "APPLIES_DURING", "aborted start", context="the driver who caused it and fails to start from the pit lane")
add_fact("B5.8.3", "aborted start", "APPLIES_DURING", TT, context="each one shortens the TTCS by one lap")
add_fact("B5.9.1", "race director", "CONTROLS", "extra formation lap", context="for a problem that does not require an aborted start")
add_fact("B5.9.1", "extra formation lap message", "SIGNALS", "extra formation lap", context="orange lights on the start gantry, then green lights 2 s later")
add_fact("B5.9.3", "race director", "CONTROLS", "extra formation lap", context="may order another one")
add_fact("B5.9.4", "pit lane start", "APPLIES_DURING", "extra formation lap", context="the driver who caused it")
add_fact("B5.9.4", SG, "APPLIES_DURING", "extra formation lap", context="the driver who caused it and fails to start from the pit lane")
add_fact("B5.9.5", "extra formation lap", "APPLIES_DURING", TT, context="each one shortens the TTCS by one lap")
add_fact("B5.9.6", "extra formation lap", "APPLIES_DURING", TT, context="the TTCS still counts for the Championship however often it is repeated")
add_fact("B5.10.1", "race director", "CONTROLS", "formation lap behind safety car")
add_fact("B5.10.1", "formation lap behind safety car message", "SIGNALS", "formation lap behind safety car")
add_fact("B5.10.1", "safety car orange lights", "SIGNALS", "formation lap behind safety car", context="lit at the ten minute signal if wet tyres are mandated, otherwise at the five minute signal")
add_fact("B5.10.1", "formation lap behind safety car", "REQUIRES", "wet-weather tyre", context="if mandated by the race director")
add_fact("B5.10.2", "race director", "CONTROLS", "safety car", context="max gap 10 car lengths, may raise it to 20 in poor visibility")
add_fact("B5.10.5", "pit lane start", "APPLIES_DURING", "formation lap behind safety car", context="any car entering the pit lane during these laps, other than to follow the safety car")
add_fact("B5.10.6", "overtaking", "APPLIES_DURING", "formation lap behind safety car", context="only to restore the starting order: delayed car, delayed pit lane starter, or a car with an obvious problem")
add_fact("B5.10.6", SG, "APPLIES_DURING", "standing start", context="delayed driver who hasn't restored position by the first safety car line and doesn't re-enter the pit lane")
add_fact("B5.10.6", "overtaking", "APPLIES_DURING", "rolling start", context="a delayed car may restore its position only before the ROLLING START message")
add_fact("B5.10.7", "formation lap behind safety car", "APPLIES_DURING", "sprint", "race", context="TTCS shortened by the safety car laps minus one")
add_fact("B5.10.8", "standing start message", "SIGNALS", "standing start", context="panels show SS, pit exit closes, safety car orange lights off; SC enters the pits at the end of the lap")
add_fact("B5.10.8", "standing start", "REQUIRES", "start procedure", context="cars return to their grid positions and follow B5.7")
add_fact("B5.10.8", SG, "APPLIES_DURING", "standing start", context="pit lane starter who fails to start from the pit lane")
add_fact("B5.10.8", "race director", "CONTROLS", "extra formation lap")
add_fact("B5.10.9", "rolling start message", "SIGNALS", "rolling start", context="panels show RS, pit exit closes, safety car orange lights off")
add_fact("B5.10.9", "green flag", "SIGNALS", "rolling start", context="at the control line as the safety car approaches the pit entry road")
add_fact("B5.10.9", "overtaking", "APPLIES_DURING", "rolling start", context="forbidden until the control line after the safety car enters the pit entry road; no driving alongside")
add_fact("B5.10.9", SG, "APPLIES_DURING", "rolling start", context="pit lane starter who fails to start from the pit lane")
add_fact("B5.11.1", "false start", "PUNISHABLE_BY", *PEN4, context="at the stewards' discretion")
add_fact("B5.11.1", "steward", "MAY_IMPOSE", *PEN4, context="false start")
add_fact("B5.11.1", "false start", "APPLIES_DURING", "standing start", "standing start resumption", context="car must be stationary from the third red light, detectable by its transponder, front tyres inside the grid box lines")
add_fact("B5.12", "double waved yellow flag", "SIGNALS", "virtual safety car", context="VSC is used when double waved yellows are needed and people may be in danger, but a safety car is not warranted")
add_fact("B5.12.1", "race director", "CONTROLS", "virtual safety car")
add_fact("B5.12.1", "vsc deployed message", "SIGNALS", "virtual safety car", context="FIA light panels show VSC")
add_fact("B5.12.1", "virtual safety car", "APPLIES_DURING", TT, context="neutralises a TTCS")
add_fact("B5.12.2", "minimum time breach", "PUNISHABLE_BY", *PEN4, context="under the VSC during a TTCS")
add_fact("B5.12.2", "steward", "MAY_IMPOSE", *PEN4, context="minimum time breach under the VSC")
add_fact("B5.12.2", "minimum time breach", "APPLIES_DURING", "virtual safety car", context="must stay above the FIA ECU minimum time once in each marshalling sector and at both safety car lines")
add_fact("B5.12.2", "overtaking", "APPLIES_DURING", "virtual safety car", context=VSC_EXC)
add_fact("B5.12.2", "erratic driving", "APPLIES_DURING", "virtual safety car", context="on track, pit entry road or pit lane")
add_fact("B5.12.3", "pit stop", "APPLIES_DURING", "virtual safety car", context="during a TTCS, cars may enter the pits only to change tyres")
add_fact("B5.12.4", "race director", "CONTROLS", "virtual safety car", context="ends it when safe")
add_fact("B5.12.4", "vsc ending message", "SIGNALS", "virtual safety car", context="ends it; panels turn green 10-15 s later, green lights off after 30 s")
add_fact("B5.12.5", "virtual safety car", "APPLIES_DURING", TT, context="laps under the VSC count as laps")
add_fact("B5.13", "safety car period", "APPLIES_DURING", TT, context="used only when people are in immediate physical danger but a suspension is not needed")
add_fact("B5.13.1", "race director", "CONTROLS", "safety car period")
add_fact("B5.13.1", "safety car deployed message", "SIGNALS", "safety car period")
add_fact("B5.13.1", "fia light panel", "SIGNALS", "safety car period", context="show SC")
add_fact("B5.13.1", "waved yellow flag", "SIGNALS", "safety car period", context="waved at all marshal posts with SC boards")
add_fact("B5.13.1", "sc board", "SIGNALS", "safety car period")
add_fact("B5.13.1", "safety car orange lights", "SIGNALS", "safety car period", context="safety car joins the track with orange lights on, wherever the leader is")
add_fact("B5.13.2", "minimum time breach", "PUNISHABLE_BY", *PEN4, context="under the safety car, until crossing the first safety car line for the second time")
add_fact("B5.13.2", "steward", "MAY_IMPOSE", *PEN4, context="minimum time breach under the safety car")
add_fact("B5.13.2", "minimum time breach", "APPLIES_DURING", "safety car period")
add_fact("B5.13.2", "overtaking", "APPLIES_DURING", "safety car period", context="forbidden (including the safety car) until the control line after the SC enters the pit entry road; exceptions include the SC green light, pit entry/exit, the SC returning, cars stopping at their garage, or a car with an obvious problem")
add_fact("B5.13.2", "erratic driving", "APPLIES_DURING", "safety car period", context="on track, pit entry road or pit lane")
add_fact("B5.13.2", "race director", "CONTROLS", "safety car", context="max gap 10 car lengths, may raise it to 20 in poor visibility")
add_fact("B5.13.2", "low visibility message", "SIGNALS", "safety car period", context="max gap increased to 20 car lengths")
add_fact("B5.13.2", "safety car green light", "SIGNALS", "overtaking", context="a driver signalled from the safety car may overtake")
add_fact("B5.13.3", "race director", "CONTROLS", "safety car period", context="may send the safety car and the field through the pit lane")
add_fact("B5.13.3", DT, "APPLIES_DURING", "safety car period", context="driver who fails to enter the pit lane when the field is sent through it")
add_fact("B5.13.3", "pit stop", "APPLIES_DURING", "safety car period", context="only to change tyres, unless the field is sent through the pit lane")
add_fact("B5.13.4", "safety car green light", "SIGNALS", "overtaking", context="cars between the safety car and the leader, or lapped cars, must pass")
add_fact("B5.13.4", "lapped cars may now overtake message", "SIGNALS", "overtaking", context="lapped cars pass the lead-lap cars and the safety car, then rejoin the back of the queue")
add_fact("B5.13.4", "overtaking will not be permitted message", "SIGNALS", "overtaking", context="track unsuitable for overtaking")
add_fact("B5.13.4", "race director", "CONTROLS", "overtaking", context="decides when lapped cars may overtake")
add_fact("B5.13.4", "race director", "CONTROLS", "pit lane exit", context="may close it while the safety car queue passes")
add_fact("B5.13.5", "lapped cars may now overtake message", "SIGNALS", "safety car period", context="safety car returns at the end of the following lap unless still needed")
add_fact("B5.13.6", "race director", "CONTROLS", "safety car period", context="ends it when safe")
add_fact("B5.13.6", "safety car in this lap message", "SIGNALS", "safety car period", context="ends it; safety car enters the pits at the end of the lap")
add_fact("B5.13.6", "safety car orange lights", "SIGNALS", "safety car period", context="extinguished: the SC comes in this lap; the leader sets the pace, no erratic driving or running alongside")
add_fact("B5.13.6", "green flag", "SIGNALS", "safety car period", context="shown at the control line as the leader approaches (not on the last lap)")
add_fact("B5.13.7", "safety car period", "APPLIES_DURING", TT, context="laps behind the safety car count")
add_fact("B5.13.8", "race director", "CONTROLS", "safety car", context="decides whether it stays out after the end-of-session signal and leads the cars to parc fermé")
add_fact("B5.13.8", "overtaking", "APPLIES_DURING", "safety car period", context="last lap: cars take the chequered flag without overtaking")
add_fact("B5.14.1", "starting procedure suspended message", "SIGNALS", "starting procedure suspension")
add_fact("B5.14.1", "red flag", "SIGNALS", "starting procedure suspension", context="at all marshal posts and the control line")
add_fact("B5.14.1", "starting procedure suspension", "OCCURS_AT", "fast lane", context="cars line up in the order they entered behind the safety car; on the grid if the pit entry is closed")
add_fact("B5.14.1", "starting procedure suspension", "PRECEDES", "resumption procedure")
add_fact("B5.14.2", "race director", "CONTROLS", "suspension")
add_fact("B5.14.2", "red flag", "SIGNALS", "suspension", context="RED FLAG - SPRINT/RACE SUSPENDED message; red flags at all marshal posts; pit exit closed")
add_fact("B5.14.2", "overtaking", "APPLIES_DURING", "suspension", context="forbidden")
add_fact("B5.14.2", "suspension", "OCCURS_AT", "fast lane", context="cars line up in arrival order; on the grid if the pit entry is closed")
add_fact("B5.14.2", "suspension", "PRECEDES", "resumption procedure")
add_fact("B5.14.2", "suspension", "APPLIES_DURING", "sprint", "race", context="the clock keeps running and the suspension is added to the maximum time; if not resumed, results from the penultimate lap")
add_fact("B5.14.3", "resumption procedure suspended message", "SIGNALS", "resumption procedure suspension")
add_fact("B5.14.3", "red flag", "SIGNALS", "resumption procedure suspension", context="at all marshal posts and the control line")
add_fact("B5.14.3", "resumption procedure suspension", "OCCURS_AT", "fast lane", context="cars line up in arrival order; on the grid if the pit entry is closed")
add_fact("B5.14.3", "resumption procedure suspension", "PRECEDES", "resumption procedure")
WORK = "permitted fast-lane work during a suspension"
add_fact("B5.14.4", "tyre", "APPLIES_DURING", "suspension", "starting procedure suspension", "resumption procedure suspension", context=WORK + ": wheels and tyres may be changed")
add_fact("B5.14.4", "front wing profile", "APPLIES_DURING", "suspension", context=WORK + ": position may be adjusted")
add_fact("B5.14.4", "driver cooling system", "APPLIES_DURING", "suspension", context=WORK + ": cooling medium may be replaced if a Heat Hazard is declared")
add_fact("B5.14.4", "fia", "CONTROLS", "f1 car", context="cars may not leave the fast lane during a suspension unless asked by the FIA; moved cars go to the back of the line")
add_fact("B5.15.1", "resumption order", "APPLIES_DURING", "resumption procedure", context="cars from the garage or moved from the fast lane go to the back; Competitors told before the ten minute signal")
add_fact("B5.15.1", "suspension", "DETERMINES", "resumption order", context="order at the last point when all positions could be determined")
add_fact("B5.15.1", "starting procedure suspension", "DETERMINES", "resumption order", context="order of entering the pit lane; cars penalised to start from the pit lane at the back")
add_fact("B5.15.1", "resumption procedure suspension", "DETERMINES", "resumption order", context="order of entering the pit lane behind the safety car")
add_fact("B5.15.1", "safety car", "OCCURS_AT", "fast lane", context="at the front of the line during the suspension")
add_fact("B5.15.2", "resumption procedure", "REQUIRES", "official messaging system", context="resumption time announced with at least 10 min warning")
for g in SIG5:
    add_fact("B5.15.2", g, "SIGNALS", "resumption procedure", context="countdown to the resumption, each with an audible warning")
add_fact("B5.15.2", "safety car lights on message", "SIGNALS", "resumption procedure", context="at the five minute signal, or the ten minute signal if wet tyres are mandated")
add_fact("B5.15.2", "resumption procedure", "REQUIRES", "wet-weather tyre", context="if the race director mandates them at the ten minute signal")
add_fact("B5.15.2", "wheels not fitted at five minute signal", "PUNISHABLE_BY", SG, context="resumption: wheels not fitted at 5 min, or changed before first leaving the pit lane")
add_fact("B5.15.2", "personnel on grid after fifteen second signal", "PUNISHABLE_BY", "pit lane start", context="resumption: car in the fast lane joins from the end of the pit lane")
add_fact("B5.15.2", "personnel on grid after fifteen second signal", "PUNISHABLE_BY", SG, context="resumption: if the driver then fails to resume from the pit lane")
add_fact("B5.15.2", "race director", "CONTROLS", "standing start resumption", "rolling start resumption", context="decides which, when safe")
add_fact("B5.15.2", "resumption procedure", "APPLIES_DURING", TT, context="laps behind the safety car count; cars between the SC and the leader and lapped cars do a further lap 2 min before")
add_fact("B5.15.3", "overtaking", "APPLIES_DURING", "standing start resumption", "rolling start resumption", context="laps behind the safety car: only to restore the resumption order (delayed car or obvious problem)")
add_fact("B5.15.3", "unauthorised overtaking", "PUNISHABLE_BY", DT, SG, context="unnecessary overtaking during the laps behind the safety car at the resumption")
add_fact("B5.15.3", "steward", "MAY_IMPOSE", DT, SG, context="unauthorised overtaking at the resumption")
add_fact("B5.15.3", SG, "APPLIES_DURING", "standing start resumption", context="delayed driver who hasn't restored position by the first safety car line and doesn't re-enter the pit lane")
add_fact("B5.15.4", "race director", "CONTROLS", "standing start resumption")
add_fact("B5.15.4", "standing start message", "SIGNALS", "standing start resumption", context="panels show SS, pit exit closed, safety car orange lights off")
add_fact("B5.15.4", "resumption order", "DETERMINES", "standing start resumption", context="grid positions; vacant if a car cannot reach the grid")
add_fact("B5.15.4", "standing start resumption", "REQUIRES", "start procedure", context="cars take their grid positions and follow B5.7")
add_fact("B5.15.4", SG, "APPLIES_DURING", "standing start resumption", context="driver who fails to resume from the pit lane when required")
add_fact("B5.15.4", "race director", "CONTROLS", "extra formation lap")
add_fact("B5.15.5", "race director", "CONTROLS", "rolling start resumption")
add_fact("B5.15.5", "rolling start message", "SIGNALS", "rolling start resumption", context="panels show RS, pit exit closed, safety car orange lights off")
add_fact("B5.15.5", "green flag", "SIGNALS", "rolling start resumption", context="at the control line as the safety car approaches the pit entry road")
add_fact("B5.15.5", "overtaking", "APPLIES_DURING", "rolling start resumption", context="forbidden until the control line after the safety car enters the pit entry road; no driving alongside")
add_fact("B5.15.5", SG, "APPLIES_DURING", "rolling start resumption", context="driver who fails to resume from the pit lane when required")
add_fact("B5.16.1", "chequered flag", "SIGNALS", "finishing procedure", context="shown at the control line on track once the leader completes the full distance")
add_fact("B5.16.2", "chequered flag", "SIGNALS", TT, context="if shown early, the TTCS ends when the leader last crossed the control line before it; if late, when it should have ended")
add_fact("B5.16.3", "marshal", "CONTROLS", "f1 car", context="takes classified cars that cannot reach parc fermé under their own power")
build("B5", MENTIONS)
