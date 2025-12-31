# Initial Concept
Du är en expert på Python UI-design och biblioteket 'rich'. Jag vill bygga "The Core CLI" – ett futuristiskt gränssnitt för min AI-assistent.

Här är min existerande stack:
1. `speak.py`: Har funktionen `speak(text)` (blockerande anrop som skickar ljud till Google Home).
2. `brain.py`: Har funktionen `ask_brain(prompt)` (returnerar strängar från min lokala LLM).

MÅL:
Skapa filen `cli.py`. Det ska vara en "Single Screen Application" som körs i terminalen med ett ljust, professionellt tema.

--- DESIGN & TEMA (Solarized Light) ---
Använd `rich.theme.Theme` med dessa färger:
- Background: #fdf6e3 (Sätts via terminalens inställningar, men anpassa textfärger för ljus bakgrund)
- Text: #657b83
- Accent (Avatar): #268bd2 (Blue) & #d33682 (Magenta) för ögon/mun.
- Waveform: #2aa198 (Cyan)
- Alert/User: #cb4b16 (Orange)

--- KOMPONENTER ---

1. KLASS: `AIAvatar`
   - Ska innehålla ASCII-konst för ett robotansikte.
   - Metod `get_frame(state)`:
     - State 'IDLE': Ögonen öppna, munnen stängd (blinkar slumpmässigt).
     - State 'TALKING': Munnen varierar mellan öppen/stängd (" o ", " - ", " O ").

2. KLASS: `Waveform`
   - Generera en sträng med block-karaktärer (  ▂ ▃ ▄ ▅ ▆ ▇ █).
   - Ska bara röra sig (slumpmässig amplitud) när systemet är i state 'TALKING'. Annars en platt linje.

3. LAYOUT (`rich.layout`)
   - Header: "DEV STATION" (Centrerad, Bold).
   - Split Main:
     - Vänster (Sidebar): Visar Avatar + Waveform.
     - Höger (Log): Panel som visar historik (User input + AI response rendered Markdown).
   - Footer: Statusrad (Modell: GPT-OSS | Output: Google Home).

--- LOGIK & THREADING (Viktigt!) ---
För att animationerna inte ska frysa när `speak()` körs (eftersom den tar tid på sig):
1. Skapa en global flagga eller Event `is_speaking`.
2. När AI:n svarar:
   - Starta en `threading.Thread` som kör `speak(text)`.
   - Sätt `is_speaking = True`.
   - I huvudloopen: Uppdatera `AIAvatar` och `Waveform` baserat på `is_speaking`.
   - När tråden är klar, sätt `is_speaking = False`.

--- INTERAKTION ---
Eftersom `input()` blockerar main thread, gör så här:
1. Använd en `while True` loop.
2. Rendera layouten en gång.
3. Ta input från användaren (animationen kan pausa här, det är ok).
4. När användaren trycker enter: Starta en `Live` context manager som visar "Thinking..." spinner och sedan animerar Avatar/Waveform medan svaret genereras och läses upp.

--- KODKRAV ---
- Använd `rich.console`, `rich.layout`, `rich.panel`, `rich.live`.
- Generera snygg ASCII-konst för roboten i koden.
- Inkludera dummy-funktioner för `speak` och `brain` om import misslyckas, så jag kan testa UI:t direkt.

Bygg hela `cli.py` nu. Gör den "Sci-Fi men ren".

# Product Guide: The Core CLI

## Vision
To build "The Core CLI", a futuristic, "Single Screen Application" interface for the local AI assistant. It transforms the terminal into a professional, "Sci-Fi but clean" command center (`DEV STATION`) that facilitates voice interaction and system monitoring with a polished user experience.

## Target Audience
- **Primary:** The Developer (Home Lab Administrator).

## Core Features
1.  **Immersive Terminal Interface:**
    -   Single-screen layout using `rich.layout`.
    -   Professional "Solarized Light" aesthetic.
2.  **Interactive AI Avatar:**
    -   ASCII-based robot face (`AIAvatar` class).
    -   Dynamic states: `IDLE` (blinking) and `TALKING` (mouth movement).
3.  **Visual Feedback:**
    -   Real-time `Waveform` visualization that reacts to speech state.
    -   History log of User Input vs. AI Response (Markdown rendered).
4.  **Non-Blocking Audio:**
    -   Threaded implementation of `speak()` to ensure UI animations remain fluid during TTS playback.
5.  **Seamless Integration:**
    -   Direct integration with existing `brain.py` (LLM) and `speak.py` (TTS).

## Design & Theme
-   **Theme:** Solarized Light (Background: `#fdf6e3`, Text: `#657b83`).
-   **Accents:** Avatar (Blue/Magenta), Waveform (Cyan), Alert (Orange).
-   **Style:** Futuristic, professional, clean.
