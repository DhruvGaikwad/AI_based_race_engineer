# AI Race Engineer

A local prototype race engineer for Assetto Corsa Competizione.

The app reads live ACC shared memory telemetry and responds through voice output. It can answer spoken driver questions and also trigger automatic alerts from live telemetry, such as lap invalidation.

## Current Features

- Reads live telemetry from Assetto Corsa Competizione.
- Listens for voice commands through your microphone.
- Replies using text-to-speech.
- Reports current speed.
- Reports race position.
- Reports the gap ahead and gap behind.
- Reports last lap time and best lap time.
- Estimates whether you have enough fuel to finish.
- Tracks lap and sector deltas against your fastest tracked lap.
- Alerts when the current lap becomes invalid.
- Reports rain intensity.

## Requirements

- Windows
- Python 3
- Assetto Corsa Competizione
- A working microphone
- ACC shared memory enabled through the game

This project uses `pyaccsharedmemory`, which is based on the ACC shared memory interface.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

Start Assetto Corsa Competizione first, then run:

```powershell
python engineer\engineer.py
```

The app will print detected microphones, start listening for commands, and speak engineer responses when telemetry is available.

## Example Commands

- "speed"
- "position"
- "gap ahead"
- "gap behind"
- "last lap time"
- "best lap time"
- "fuel"
- "time loss"
- "sector gap"
- "rain"

## Project Status

This is an early prototype. The code is intentionally simple while the core race engineer behavior is being developed.

23/04/26: Updated code with fuel report and lap tracking.
