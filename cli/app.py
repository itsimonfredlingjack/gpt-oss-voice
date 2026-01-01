"""THE CORE - Cyberpunk AI Terminal Interface.

A neo-tokyo inspired command center for interacting with
the local AI brain. Features non-blocking animations,
streaming text output, and a visually striking aesthetic.

    ◢◤ THE CORE ◥◣
    Neural Interface Online
"""

import asyncio
import time
import math
import sys
import logging
import random
from collections import deque
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
from cli.theme import SOLARIZED_LIGHT_THEME
from cli.avatar import BrailleAvatar
from cli.waveform import Waveform
from cli.layout import (
    make_layout,
    make_header,
    make_footer,
    make_sidebar_panel,
    make_log_panel,
)
from cli.raw_input import RawInputHandler, InputEvent, InputEventType
from cli.renderer import StreamingRenderer


# --- External integrations (with fallbacks) ---
try:
    from speak import GoogleHomeSpeaker, speak
except ImportError:
    class GoogleHomeSpeaker:
        """Fallback speaker for testing."""
        def speak(self, text: str) -> None:
            time.sleep(len(text) * 0.05)
        def stop(self) -> None:
            pass
    
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
        # Use Midnight Tokyo theme for supreme design
        from cli.theme import MIDNIGHT_TOKYO_THEME
        self.console = Console(theme=MIDNIGHT_TOKYO_THEME, force_terminal=True)
        
        # Set up logging (file-based, doesn't interfere with Rich display)
        logging.basicConfig(
            filename="core.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)

        # Core components
        self.state = get_state_manager()
        self.avatar = BrailleAvatar(radius=5)
        self.waveform = Waveform()
        self.layout = make_layout()
        self.input_handler = RawInputHandler()
        self.current_input = ""  # Current input text for rendering
        self.renderer = StreamingRenderer()
        
        # Voice-first: Google Home speaker instance
        try:
            self.speaker = GoogleHomeSpeaker()
        except Exception:
            # Fallback if import fails
            self.speaker = None

        # State
        self.running = True
        # Use deque with maxlen for automatic size limiting (performance optimization)
        self.history: deque[Message] = deque(maxlen=self.config.max_history)
        self.response_queue: asyncio.Queue[str] = asyncio.Queue()
        self.current_response = ""
        self.show_prompt = True
        self.boot_complete = False

        # Glitch effect counter
        self._frame_count = 0
        self._glitch_chance = 0.005
        
        # Pulse effect variables
        self._pulse_speed = 5.0

        # Performance optimization: Pre-build common strings
        self.USER_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━"
        self.AI_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━"
        self.USER_PREFIX = "◢ USER "
        self.AI_PREFIX = "◣ CORE "
        
        # Performance optimization: Cache cursor string slices
        self._last_cursor_pos = -1
        self._last_input_text = ""
        self._cached_before_cursor = ""
        self._cached_after_cursor = ""

    def run(self) -> None:
        """Main application entry point with guaranteed terminal cleanup."""
        try:
            asyncio.run(self._async_main())
        except KeyboardInterrupt:
            self._shutdown()
        except Exception as e:
            # Log unexpected errors
            self._shutdown()
            raise
        finally:
            # Guaranteed cleanup - restore terminal state
            self.input_handler.stop()
            # Ensure cursor is visible
            try:
                self.console.show_cursor()
            except Exception:
                pass  # Console might be closed

    async def _async_main(self) -> None:
        """Async main entry point."""
        await self._run_boot_sequence()
        await self._run_main_loop()

    async def _run_boot_sequence(self) -> None:
        """Display boot animation."""
        if not self.config.boot_sequence:
            self.boot_complete = True
            return

        self.console.clear()

        for frame in self.BOOT_FRAMES:
            self.console.print()
            self.console.print(
                Align.center(Text(frame, style="header")),
                highlight=False
            )
            await asyncio.sleep(0.4)

        # Scan line effect
        self.console.print()
        for _ in range(3):
            line = "─" * 50
            self.console.print(
                Align.center(Text(line, style="dim")),
                highlight=False
            )
            await asyncio.sleep(0.1)

        await asyncio.sleep(0.5)
        self.console.clear()
        self.boot_complete = True

    async def _run_main_loop(self) -> None:
        """Main render and input loop using asyncio."""
        refresh_rate = 1.0 / self.config.fps

        # Start raw input handler (sets terminal to cbreak mode)
        self.input_handler.start()

        try:
            with Live(
                self.layout,
                console=self.console,
                refresh_per_second=self.config.fps,
                screen=True,  # Use alternate buffer
                transient=True,  # Clean up on exit
                vertical_overflow="visible",  # Allow content to extend
            ) as live:
                last_frame = time.time()

                while self.running:
                    now = time.time()
                    delta = now - last_frame

                    # Frame rate limiting
                    if delta < refresh_rate:
                        await asyncio.sleep(refresh_rate - delta)

                    last_frame = time.time()
                    self._frame_count += 1

                    # Process state-specific logic
                    self._process_state()

                    # Check for input events (non-blocking, synchronous)
                    self._process_input()

                    # Check for AI responses
                    await self._process_responses()

                    # Update all visual components
                    self._update_layout()

                    live.refresh()
        finally:
            # Clean up input handler (restores terminal state)
            self.input_handler.stop()

    def _process_state(self) -> None:
        """Process current state logic with UX feedback."""
        current = self.state.state

        if current == AppState.IDLE:
            self.input_handler.enable()
            self.show_prompt = True

        elif current == AppState.THINKING:
            self.input_handler.disable()
            self.show_prompt = False

        elif current == AppState.TALKING:
            self.input_handler.disable()
            self.show_prompt = False

        elif current == AppState.ERROR:
            # Allow input to dismiss error
            self.input_handler.enable()
            self.show_prompt = False
            # Auto-recover after 5 seconds
            if self.state.duration > 5.0:
                self.state.force_state(AppState.IDLE)

    def _process_input(self) -> None:
        """Process input events from handler (synchronous)."""
        # Performance: Limit events per frame to prevent blocking
        # Process up to 10 events per frame for responsive UI
        max_events = 10
        event_count = 0
        
        while event_count < max_events:
            event = self.input_handler.get_event()
            if event is None:
                break

            event_count += 1

            if event.type == InputEventType.EXIT:
                self.running = False
                break

            elif event.type == InputEventType.INTERRUPT:
                # Ctrl+C - skip current action or exit
                if self.state.state != AppState.IDLE:
                    # Voice-first: Stop speaking if in TALKING state
                    if self.state.state == AppState.TALKING and self.speaker:
                        self.speaker.stop()
                    self.renderer.skip()
                    self.state.force_state(AppState.IDLE)
                    self.state.set_speaking_text(None)  # Clear speaking text
                    self.input_handler.clear_buffer()
                    self.current_input = ""
                else:
                    self.running = False
                    break

            elif event.type == InputEventType.TEXT:
                # Clear input buffer after submission
                self.input_handler.clear_buffer()
                # In ERROR state, any input recovers to IDLE
                if self.state.state == AppState.ERROR:
                    self.state.force_state(AppState.IDLE)
                else:
                    # Schedule async handler
                    asyncio.create_task(self._handle_user_input(event.text))
        
        # Performance: Update input text once after processing all events
        self.current_input = self.input_handler.input_text

    async def _handle_user_input(self, text: str) -> None:
        """Handle user text input.

        Args:
            text: The user's input text.
        """
        # Add to history
        self.history.append(Message(role='user', content=text))

        # Transition to thinking
        self.state.transition_to(AppState.THINKING)

        # Spawn brain task
        asyncio.create_task(self._brain_worker(text))

    async def _brain_worker(self, prompt: str) -> None:
        """Background worker that queries the AI.

        Args:
            prompt: User's prompt to send to AI.
        """
        try:
            # Run blocking brain call in executor
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, ask_brain, prompt)
            await self.response_queue.put(response)
        except Exception as e:
            # Log error for debugging
            self.logger.error(f"Brain worker failed: {e}", exc_info=True)
            # Signal error state with UX-friendly message
            # Handle specific exception types for better UX
            if "Connection" in str(type(e).__name__) or "Connection" in str(e):
                error_msg = "Cannot connect to Ollama. Is it running?"
            elif "Empty" in str(type(e).__name__) or "empty" in str(e).lower():
                error_msg = "Model returned empty response"
            else:
                error_msg = str(e)[:50] if str(e) else "Connection failed"
            self.state.set_error(f"Neural link error: {error_msg}")

    async def _process_responses(self) -> None:
        """Check for and process AI responses."""
        try:
            response = self.response_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        # Add to history (invalidate cache)
        self.history.append(Message(role='ai', content=response))
        self._rendered_messages_cache = None  # Invalidate cache

        # Start streaming the response
        if self.config.stream_text:
            self.renderer.start_stream(response)
        else:
            self.current_response = response

        # Transition to talking
        self.state.transition_to(AppState.TALKING)

        # Spawn speak task
        asyncio.create_task(self._speak_worker(response))

    async def _speak_worker(self, text: str) -> None:
        """Background worker that speaks the response.

        Args:
            text: Text to speak via TTS.
        """
        try:
            # Voice-first: Set speaking text for indicator
            self.state.set_speaking_text(text)
            
            # Run blocking speak call in executor
            loop = asyncio.get_running_loop()
            if self.speaker:
                # Use GoogleHomeSpeaker instance for interrupt capability
                await loop.run_in_executor(None, self.speaker.speak, text)
            else:
                # Fallback to function
                await loop.run_in_executor(None, speak, text)
        except Exception as e:
            # Log error for debugging
            self.logger.error(f"Audio error: {e}", exc_info=True)
            # Display error to user without stopping the flow
            # Handle specific exception types for better UX
            if "DeviceNotFound" in str(type(e).__name__) or "not found" in str(e).lower():
                error_msg = f"Device not found. Check power?"
            else:
                error_msg = str(e)[:30] if str(e) else "Device unreachable"
            self.state.set_error(f"Audio Error: {error_msg}")
        finally:
            # Voice-first: Clear speaking text
            self.state.set_speaking_text(None)
            # Wait for streaming to complete
            while not self.renderer.is_complete:
                await asyncio.sleep(0.1)
            # Return to idle
            self.state.force_state(AppState.IDLE)

    def _update_layout(self) -> None:
        """Update all layout components."""
        state_name = self.state.state_name

        # Calculate dynamic border style
        border_style = 'border'
        if state_name == 'TALKING':
            border_style = self._get_pulse_style()

        # Header with optional glitch
        if self._should_glitch():
            header = make_header("T̷H̷E̷ ̷C̷O̷R̷E̷", "◇ SIGNAL INTERFERENCE ◇", border_style=border_style)
        else:
            header = make_header("THE CORE", "◇ NEURAL INTERFACE v2.0 ◇", border_style=border_style)

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
                hint=hint,
                speaking_text=self.state.speaking_text,  # Voice-first: show speaking text
                border_style=border_style if state_name == 'TALKING' else 'border.dim'
            )
        )

        # Sidebar (Avatar + Waveform)
        avatar_text = self.avatar.render(state_name)
        # Use gradient waveform for TALKING state, regular for others
        if state_name == 'TALKING':
            waveform_text = self.waveform.get_frame_rich(state_name)
        else:
            waveform_str = self.waveform.get_frame(state_name)
            from rich.text import Text
            waveform_text = Text(waveform_str, style='waveform')

        self.layout["sidebar"].update(
            make_sidebar_panel(avatar_text, waveform_text, state_name, border_style=border_style)
        )

        # Log (Conversation)
        self.layout["log"].update(
            make_log_panel(self._render_history(), border_style=border_style)
        )

    def _render_history(self) -> Group:
        """Render conversation history.

        Returns:
            Rich Group of rendered messages.
        """
        elements = []

        # Calculate total messages for decay logic
        total_msgs = len(self.history)

        # Performance: Iterate directly over deque (no list conversion needed)
        # deque is iterable and efficient for this use case
        for index, msg in enumerate(self.history):
            # Calculate message age (0 is newest)
            age = total_msgs - 1 - index

            # Determine style based on age
            if age == 0:
                user_style = "user_input"
                ai_style = "bright_text" # Using bright_text from theme instead of markdown default
                prefix_style = "ai_label"
            elif age <= 3:
                user_style = "dim"
                ai_style = "dim"
                prefix_style = "dim"
            elif age <= 10:
                user_style = "dim" # Darker dim not easily available without custom style, using dim
                ai_style = "#444444" # dim grey30 approx
                prefix_style = "#444444"
            else:
                user_style = "#333333"
                ai_style = "#333333"
                prefix_style = "#333333"

            # Apply corruption to ancient history
            content = msg.content
            if age > 10:
                content = self._corrupt_text(content)

            if msg.role == 'user':
                text = Text()
                # Fix visual regression: User prefix should use user_style, not prefix_style (which is for AI)
                text.append(self.USER_PREFIX, style=user_style)
                text.append(self.USER_SEPARATOR, style="dim")
                elements.append(text)
                elements.append(
                    Padding(Text(content, style=user_style), (0, 0, 1, 2))
                )

            elif msg.role == 'ai':
                text = Text()
                text.append(self.AI_PREFIX, style=prefix_style)
                text.append(self.AI_SEPARATOR, style="dim")
                elements.append(text)

                # Use streaming text if this is the current response
                # Performance: Check if this is the last message efficiently
                is_last = msg is self.history[-1] if self.history else False
                if is_last and self.renderer.is_streaming:
                    stream_content = self.renderer.current_text
                    # Add cursor blink effect
                    if self._frame_count % 10 < 5:
                        stream_content += "▊"
                    elements.append(
                        Padding(Markdown(stream_content), (0, 0, 1, 2))
                    )
                else:
                    # Apply manual styling for decayed messages instead of Markdown
                    # to control the color properly
                    if age == 0:
                         elements.append(
                            Padding(Markdown(content), (0, 0, 1, 2))
                        )
                    else:
                        elements.append(
                            Padding(Text(content, style=ai_style), (0, 0, 1, 2))
                        )

        # Show input prompt when idle
        if self.show_prompt and self.state.state == AppState.IDLE:
            prompt = Text()
            prompt.append("\n◈ ", style="user_prompt")
            
            # Show current input text if any
            if self.current_input:
                # Voice-first: Render cursor at correct position
                cursor_pos = self.input_handler.cursor_position
                
                # Performance: Cache string slices to avoid repeated slicing
                if (cursor_pos != self._last_cursor_pos or 
                    self.current_input != self._last_input_text):
                    self._cached_before_cursor = self.current_input[:cursor_pos]
                    self._cached_after_cursor = self.current_input[cursor_pos:]
                    self._last_cursor_pos = cursor_pos
                    self._last_input_text = self.current_input
                
                prompt.append(self._cached_before_cursor, style="user_input")
                # Blinking cursor at position
                if self._frame_count % 15 < 8:
                    prompt.append("▊", style="user_cursor")
                else:
                    prompt.append(" ", style="user_input")  # Invisible when not blinking
                prompt.append(self._cached_after_cursor, style="user_input")
            else:
                prompt.append("AWAITING INPUT", style="dim")
                # Blinking cursor at end
                if self._frame_count % 15 < 8:
                    prompt.append(" ▊", style="user_prompt")
            
            prompt.append(" ◈", style="user_prompt")

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
        return random.random() < self._glitch_chance

    def _get_pulse_style(self) -> str:
        """Generate a pulsing border color style based on time.

        Alternates between Neon Cyan (#00f3ff) and Neon Pink (#ff00ff).

        Returns:
            A rich style string with the calculated color.
        """
        t = (math.sin(time.time() * self._pulse_speed) + 1) / 2  # 0.0 to 1.0

        # Cyan: 0, 243, 255
        # Pink: 255, 0, 255

        r = int(t * 255)
        g = int((1 - t) * 243)
        b = 255

        return f"bold #{r:02x}{g:02x}{b:02x}"

    def _corrupt_text(self, text: str) -> str:
        """Apply visual corruption to text.

        Args:
            text: The text to corrupt.

        Returns:
            Corrupted text string.
        """
        chars = list(text)
        length = len(chars)

        # Corrupt 10% of characters randomly per frame
        # This creates a "digital rain" effect for ancient history
        num_corrupt = max(1, length // 10)

        for _ in range(num_corrupt):
            idx = random.randint(0, length - 1)
            if chars[idx] not in "\n\t ": # Don't corrupt whitespace heavily
                chars[idx] = random.choice([".", "0", "1", "⁖", "x", "+"])

        return "".join(chars)

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

import threading
import queue

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
