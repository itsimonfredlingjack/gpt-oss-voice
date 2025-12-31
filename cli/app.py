"""THE CORE - Cyberpunk AI Terminal Interface.

A neo-tokyo inspired command center for interacting with
the local AI brain. Features non-blocking animations,
streaming text output, and a visually striking aesthetic.

    ◢◤ THE CORE ◥◣
    Neural Interface Online
"""

import threading
import queue
import time
import sys
from typing import Optional, List
from dataclasses import dataclass, field

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.padding import Padding
from rich.markdown import Markdown

# Local imports
from cli.state import StateManager, AppState, get_state_manager
from cli.theme import CYBERPUNK_THEME
from cli.avatar import AIAvatar
from cli.waveform import Waveform
from cli.layout import (
    make_layout,
    make_header,
    make_footer,
    make_sidebar_panel,
    make_log_panel,
)
from cli.input_handler import InputHandler, InputEvent, InputEventType
from cli.renderer import StreamingRenderer


# --- External integrations (with fallbacks) ---
try:
    from speak import speak
except ImportError:
    def speak(text: str) -> None:
        """Fallback: simulate speaking delay."""
        time.sleep(len(text) * 0.05)

try:
    from brain import ask_brain
except ImportError:
    def ask_brain(prompt: str) -> str:
        """Fallback: mock AI response."""
        time.sleep(1.5)
        return f"Neural response to: {prompt}"


# --- Configuration ---
@dataclass
class AppConfig:
    """Application configuration."""
    fps: int = 15
    model_name: str = "GPT-OSS"
    output_device: str = "Google Home"
    max_history: int = 50
    stream_text: bool = True
    boot_sequence: bool = True


# --- Conversation History ---
@dataclass
class Message:
    """A conversation message."""
    role: str  # 'user' or 'ai'
    content: str
    timestamp: float = field(default_factory=time.time)


# --- Main Application ---
class CLIApp:
    """The Core - Cyberpunk AI Terminal.

    Orchestrates the terminal UI with non-blocking input,
    animated avatar, and streaming AI responses.
    """

    BOOT_FRAMES = [
        "◢ INITIALIZING NEURAL LINK ◣",
        "◢◤ SYNCING CONSCIOUSNESS ◥◣",
        "◢◤◢ LOADING PERSONALITY MATRIX ◣◥◣",
        "◢◤◢◤ THE CORE ONLINE ◥◣◥◣",
    ]

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the application.

        Args:
            config: Optional configuration override.
        """
        self.config = config or AppConfig()
        self.console = Console(theme=CYBERPUNK_THEME, force_terminal=True)

        # Core components
        self.state = get_state_manager()
        self.avatar = AIAvatar()
        self.waveform = Waveform()
        self.layout = make_layout()
        self.input_handler = InputHandler()
        self.renderer = StreamingRenderer()

        # State
        self.running = True
        self.history: List[Message] = []
        self.response_queue: queue.Queue[str] = queue.Queue()
        self.current_response = ""
        self.show_prompt = True
        self.boot_complete = False

        # Glitch effect counter
        self._frame_count = 0
        self._glitch_chance = 0.005

    def run(self) -> None:
        """Main application entry point."""
        try:
            self._run_boot_sequence()
            self._run_main_loop()
        except KeyboardInterrupt:
            self._shutdown()
        finally:
            self.input_handler.stop()

    def _run_boot_sequence(self) -> None:
        """Display boot animation."""
        if not self.config.boot_sequence:
            self.boot_complete = True
            return

        self.console.clear()

        for i, frame in enumerate(self.BOOT_FRAMES):
            self.console.print()
            self.console.print(
                Align.center(Text(frame, style="header")),
                highlight=False
            )
            time.sleep(0.4)

        # Scan line effect
        self.console.print()
        for _ in range(3):
            line = "─" * 50
            self.console.print(
                Align.center(Text(line, style="dim")),
                highlight=False
            )
            time.sleep(0.1)

        time.sleep(0.5)
        self.console.clear()
        self.boot_complete = True

    def _run_main_loop(self) -> None:
        """Main render and input loop."""
        self.input_handler.start()
        refresh_rate = 1.0 / self.config.fps

        with Live(
            self.layout,
            console=self.console,
            refresh_per_second=self.config.fps,
            screen=True,
        ) as live:
            last_frame = time.time()

            while self.running:
                now = time.time()
                delta = now - last_frame

                # Frame rate limiting
                if delta < refresh_rate:
                    time.sleep(refresh_rate - delta)

                last_frame = time.time()
                self._frame_count += 1

                # Process state-specific logic
                self._process_state()

                # Check for input events (non-blocking)
                self._process_input()

                # Check for AI responses
                self._process_responses()

                # Update all visual components
                self._update_layout()

                live.refresh()

    def _process_state(self) -> None:
        """Process current state logic with UX feedback."""
        current = self.state.state

        if current == AppState.IDLE:
            self.input_handler.enable_input()
            self.show_prompt = True

        elif current == AppState.THINKING:
            self.input_handler.disable_input()
            self.show_prompt = False

        elif current == AppState.TALKING:
            self.input_handler.disable_input()
            self.show_prompt = False

        elif current == AppState.ERROR:
            # Allow input to dismiss error
            self.input_handler.enable_input()
            self.show_prompt = False
            # Auto-recover after 5 seconds
            if self.state.duration > 5.0:
                self.state.force_state(AppState.IDLE)

    def _process_input(self) -> None:
        """Process input events from handler."""
        event = self.input_handler.get_event()

        if event is None:
            return

        if event.type == InputEventType.EXIT:
            self.running = False

        elif event.type == InputEventType.INTERRUPT:
            # Ctrl+C - skip current action or exit
            if self.state.state != AppState.IDLE:
                self.renderer.skip()
                self.state.force_state(AppState.IDLE)
            else:
                self.running = False

        elif event.type == InputEventType.TEXT:
            # In ERROR state, any input recovers to IDLE
            if self.state.state == AppState.ERROR:
                self.state.force_state(AppState.IDLE)
            else:
                self._handle_user_input(event.text)

    def _handle_user_input(self, text: str) -> None:
        """Handle user text input.

        Args:
            text: The user's input text.
        """
        # Add to history
        self.history.append(Message(role='user', content=text))

        # Transition to thinking
        self.state.transition_to(AppState.THINKING)

        # Spawn brain thread
        thread = threading.Thread(
            target=self._brain_worker,
            args=(text,),
            daemon=True,
            name="BrainWorker"
        )
        thread.start()

    def _brain_worker(self, prompt: str) -> None:
        """Background worker that queries the AI.

        Args:
            prompt: User's prompt to send to AI.
        """
        try:
            response = ask_brain(prompt)
            self.response_queue.put(response)
        except Exception as e:
            # Signal error state with UX-friendly message
            error_msg = str(e)[:50] if str(e) else "Connection failed"
            self.state.set_error(f"Neural link error: {error_msg}")

    def _process_responses(self) -> None:
        """Check for and process AI responses."""
        try:
            response = self.response_queue.get_nowait()
        except queue.Empty:
            return

        # Add to history
        self.history.append(Message(role='ai', content=response))

        # Start streaming the response
        if self.config.stream_text:
            self.renderer.start_stream(response)
        else:
            self.current_response = response

        # Transition to talking
        self.state.transition_to(AppState.TALKING)

        # Spawn speak thread
        thread = threading.Thread(
            target=self._speak_worker,
            args=(response,),
            daemon=True,
            name="SpeakWorker"
        )
        thread.start()

    def _speak_worker(self, text: str) -> None:
        """Background worker that speaks the response.

        Args:
            text: Text to speak via TTS.
        """
        try:
            speak(text)
        finally:
            # Wait for streaming to complete
            while not self.renderer.is_complete:
                time.sleep(0.1)
            # Return to idle
            self.state.force_state(AppState.IDLE)

    def _update_layout(self) -> None:
        """Update all layout components."""
        state_name = self.state.state_name

        # Header with optional glitch
        if self._should_glitch():
            header = make_header("T̷H̷E̷ ̷C̷O̷R̷E̷", "◇ SIGNAL INTERFERENCE ◇")
        else:
            header = make_header("THE CORE", "◇ NEURAL INTERFACE v2.0 ◇")

        self.layout["header"].update(header)

        # Footer with UX-friendly status
        status = self.state.status_message
        hint = self.state.hint

        # Add duration indicator for THINKING state
        if state_name == "THINKING":
            duration = int(self.state.duration)
            dots = "●" * ((self._frame_count // 5) % 4)
            status = f"◇ PROCESSING {duration}s {dots}"
        elif state_name == "ERROR":
            error_msg = self.state.last_error or "Unknown error"
            status = f"✗ {error_msg[:30]}"

        self.layout["footer"].update(
            make_footer(
                model=self.config.model_name,
                output=self.config.output_device,
                status=status,
                hint=hint
            )
        )

        # Sidebar (Avatar + Waveform)
        avatar_text = self.avatar.render(state_name)
        waveform_str = self.waveform.get_frame(state_name)

        self.layout["sidebar"].update(
            make_sidebar_panel(avatar_text, waveform_str, state_name)
        )

        # Log (Conversation)
        self.layout["log"].update(
            make_log_panel(self._render_history())
        )

    def _render_history(self) -> Group:
        """Render conversation history.

        Returns:
            Rich Group of rendered messages.
        """
        elements = []

        # Get recent history
        recent = self.history[-self.config.max_history:]

        for msg in recent:
            if msg.role == 'user':
                text = Text()
                text.append("◢ USER ", style="user_input")
                text.append("━━━━━━━━━━━━━━━━━━━━━", style="dim")
                elements.append(text)
                elements.append(
                    Padding(Text(msg.content, style="user_input"), (0, 0, 1, 2))
                )

            elif msg.role == 'ai':
                text = Text()
                text.append("◣ CORE ", style="ai_label")
                text.append("━━━━━━━━━━━━━━━━━━━━━", style="dim")
                elements.append(text)

                # Use streaming text if this is the current response
                if msg == recent[-1] and self.renderer.is_streaming:
                    content = self.renderer.current_text
                    # Add cursor blink effect
                    if self._frame_count % 10 < 5:
                        content += "▊"
                else:
                    content = msg.content

                elements.append(
                    Padding(Markdown(content), (0, 0, 1, 2))
                )

        # Show input prompt when idle
        if self.show_prompt and self.state.state == AppState.IDLE:
            prompt = Text()
            prompt.append("\n◈ ", style="user_prompt")
            prompt.append("AWAITING INPUT", style="dim")
            prompt.append(" ◈", style="user_prompt")

            # Blinking cursor
            if self._frame_count % 15 < 8:
                prompt.append(" ▊", style="user_prompt")

            elements.append(Align.center(prompt))

        if not elements:
            # Empty state
            empty = Text()
            empty.append("\n\n", style="dim")
            empty.append("◇ NEURAL LINK ESTABLISHED ◇\n", style="header")
            empty.append("Type your query to begin transmission\n", style="dim")
            elements.append(Align.center(empty))

        return Group(*elements)

    def _should_glitch(self) -> bool:
        """Determine if a glitch effect should trigger.

        Returns:
            True if glitch should occur.
        """
        import random
        return random.random() < self._glitch_chance

    def _shutdown(self) -> None:
        """Clean shutdown sequence."""
        self.running = False
        self.console.clear()
        self.console.print()
        self.console.print(
            Align.center(Text("◢◤ NEURAL LINK TERMINATED ◥◣", style="warning"))
        )
        self.console.print()


# --- Backward Compatibility Exports ---
# These maintain compatibility with the old cli.py interface

APP_STATE = "IDLE"  # Deprecated: use StateManager
response_queue: queue.Queue = queue.Queue()
is_speaking = False
_speaking_lock = threading.Lock()


def get_is_speaking() -> bool:
    """Get speaking state (deprecated)."""
    with _speaking_lock:
        return is_speaking


def set_is_speaking(value: bool) -> None:
    """Set speaking state (deprecated)."""
    global is_speaking
    with _speaking_lock:
        is_speaking = value


def set_app_state(new_state: str) -> None:
    """Set app state (deprecated)."""
    global APP_STATE
    APP_STATE = new_state


def speak_threaded(text: str) -> None:
    """Speak in background thread (deprecated)."""
    set_is_speaking(True)

    def worker():
        try:
            speak(text)
        finally:
            set_is_speaking(False)
            set_app_state("IDLE")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def run_cli() -> None:
    """Run the CLI application."""
    app = CLIApp()
    app.run()


# Allow direct execution
if __name__ == "__main__":
    run_cli()
