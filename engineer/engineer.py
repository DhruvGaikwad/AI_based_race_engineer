import threading
import time
import speech_recognition as sr
import pyttsx3
from telementry import read_telemetry, close_telemetry

recognizer = sr.Recognizer()

latest_sm = None
latest_command = None  #EVERYTHING IS NONE BECAUSE WE DONT HAVE DATA YET 
running = True


def speak(message):
    print(f"Engineer: {message}")
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
        engine.stop()
    except Exception as exc:
        print(f"Speech error: {exc}")


def print_microphone_status():
    try:
        mic_names = sr.Microphone.list_microphone_names()
    except OSError as exc:
        print(f"Microphone check failed: {exc}")
        return False

    if not mic_names:
        print("No microphones detected.")
        return False

    print("Microphones detected:")
    for index, name in enumerate(mic_names):
        print(f"[{index}] {name}")

    default_mic = mic_names[0]
    print(f"Default microphone: {default_mic}")
    return True


def listen_loop():
    global latest_command

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        while running:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                command = recognizer.recognize_google(audio).lower()
                latest_command = command
                print(f"You said: {command}")

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Speech recognition service unavailable.")
#LAP TRACKING VARIABLES
previous_sector = None
lap_gap = None
sector1_gap = None
sector2_gap = None
sector3_gap = None
sector1 = None
sector2 = None
sector3 = None

previous_completed_laps = 0

best_lap = None
best_sector1 = None
best_sector2 = None
best_sector3 = None
fastest_lap_number = None
compared_lap_number = None
last_lost_sector = None


def lap_tracking(sm):
    global previous_sector, previous_completed_laps
    global sector1, sector2, sector3
    global best_lap, best_sector1, best_sector2, best_sector3
    global lap_gap, sector1_gap, sector2_gap, sector3_gap
    global fastest_lap_number, compared_lap_number, last_lost_sector

    last_sector = sm.Graphics.last_sector_time / 1000
    current_sector = sm.Graphics.current_sector_index
    completed_laps = sm.Graphics.completed_lap
    last_lap_time = sm.Graphics.last_time / 1000

    if previous_sector is None:
        previous_sector = current_sector
        previous_completed_laps = completed_laps
        return

    if current_sector != previous_sector:
        if current_sector == 1:
            sector1 = last_sector
        elif current_sector == 2:
            sector2 = last_sector
        elif current_sector == 0:
            sector3 = last_sector

        previous_sector = current_sector

    if completed_laps != previous_completed_laps:
        if sector1 is not None and sector2 is not None and sector3 is not None and last_lap_time > 0:
            compared_lap_number = completed_laps

            if best_lap is not None:
                lap_gap = last_lap_time - best_lap
                sector1_gap = sector1 - best_sector1
                sector2_gap = sector2 - best_sector2
                sector3_gap = sector3 - best_sector3

                sector_gaps = {
                    1: sector1_gap,
                    2: sector2_gap,
                    3: sector3_gap,
                }
                last_lost_sector = max(sector_gaps, key=sector_gaps.get)

            if best_lap is None or last_lap_time < best_lap:
                best_lap = last_lap_time
                best_sector1 = sector1
                best_sector2 = sector2
                best_sector3 = sector3
                fastest_lap_number = completed_laps

        sector1 = None
        sector2 = None
        sector3 = None
        previous_completed_laps = completed_laps

def fuel_report(sm):
    fuel_left = sm.Physics.fuel
    fuel_per_lap = sm.Graphics.fuel_per_lap
    session_time_remaining = sm.Graphics.session_time_left / 1000
    estimated_lap_time = sm.Graphics.estimated_lap_time / 1000

    if estimated_lap_time <= 0 or fuel_per_lap <= 0:
        return "I do not have enough fuel data yet."
    

    remaining_laps = (session_time_remaining / estimated_lap_time) + 1
    fuel_needed = remaining_laps * fuel_per_lap

    # ok so this one is a doozy we will calculate the actual fuel needed to finish the race
    # because if the needed fuel is 30 L to finish the race then we dont add 30 L again
    # because the car might already have like letts say 20 L in the tank and we need total 30
    # so we calculate the actual fuel to add by sub fuel_left from fuel_needed to avoid overadding fuel XD
    # fun fun funnnnnnnnnn

    if fuel_needed > fuel_left:
        fuel_to_add = fuel_needed - fuel_left
        return f"You need to add {fuel_to_add:.1f} litres of fuel."

    return "You have enough fuel to finish the race."




mic_ready = print_microphone_status()
listener = threading.Thread(target=listen_loop, daemon=True)
if mic_ready:
    listener.start()
else:
    print("Voice commands are disabled until a microphone is detected.")

try:
    while True:
        sm = read_telemetry()

        if sm is not None:
            latest_sm = sm
            lap_tracking(latest_sm)

        if latest_command and latest_sm is not None:
            command = latest_command
            latest_command = None
                                    #we use .1f to round to 1 decimal place, and .0f to round to whole number
                                    #we also divide gap times by 1000 to convert from milliseconds to seconds
            if "fuel" in command:
                speak(f"Estimated fuel laps remaining: {latest_sm.Graphics.fuel_estimated_laps:.1f}")

            elif "speed" in command:
                speak(f"Current speed is {latest_sm.Physics.speed_kmh:.0f} kilometers per hour")

            elif "position" in command:
                speak(f"You are in position {latest_sm.Graphics.position}")

            elif "gap ahead" in command or "ahead" in command:
                gap_ahead = latest_sm.Graphics.gap_ahead / 1000
                speak(f"Gap ahead is {gap_ahead:.1f} seconds")

            elif "gap behind" in command or "behind" in command:
                gap_behind = latest_sm.Graphics.gap_behind / 1000
                speak(f"Gap behind is {gap_behind:.1f} seconds")

            elif "last lap time " in command :
                lap_time =latest_sm.Graphics.last_time / 1000
                speak(f"last lap time was {lap_time:.1f} seconds ")
            
            elif "best lap time" in command:
                best_lap=latest_sm.Graphics.best_time / 1000
                speak(f"best time so far is {best_lap:.1f} seconds")

            elif "fuel needed " in command:
                speak(fuel_report(latest_sm))
            
            elif "time loss" in command or "lap gap" in command or "sector gap" in command:
                if lap_gap is None:
                    speak("I do not have enough lap data to compare yet.")
                else:       
                    speak(f"Lap {compared_lap_number} was {lap_gap:.1f} seconds compared to your fastest lap, lap {fastest_lap_number}.")
                    if last_lost_sector == 1:
                        speak(f"You lost the most time in sector 1, with a gap of {sector1_gap:.1f} seconds.")
                    elif last_lost_sector == 2:
                        speak(f"You lost the most time in sector 2, with a gap of {sector2_gap:.1f} seconds.")
                    elif last_lost_sector == 3:
                        speak(f"You lost the most time in sector 3, with a gap of {sector3_gap:.1f} seconds.")

            


            elif "rain" in command:
                speak(f"Rain intensity is {latest_sm.Graphics.rain_intensity.name}")

            

        time.sleep(0.1)

 

except KeyboardInterrupt:
    pass

finally:
    running = False
    close_telemetry()
