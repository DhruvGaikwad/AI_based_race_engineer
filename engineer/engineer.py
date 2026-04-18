import threading
import time
import speech_recognition as sr
import pyttsx3
from telementry import read_telemetry, close_telemetry

recognizer = sr.Recognizer()

latest_sm = None
latest_command = None
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
                lap_time = latest_sm.Graphics.last_time / 1000
                speak(f"last lap time was {lap_time:.1f} seconds ")
            
            elif "best lap time" in command:
                best_lap= latest_sm.Graphics.best_time / 1000
                speak(f"best time so far is {best_lap:.1f} seconds")

            elif "rain" in command:
                speak(f"Rain intensity is {latest_sm.Graphics.rain_intensity.name}")

            

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    running = False
    close_telemetry()
