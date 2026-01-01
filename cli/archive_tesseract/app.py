"""THE CORE - Project Tesseract Interface.

A 4D Command Center for the Neural Link.
Features a real-time Tesseract Engine, Orbital HUD, and Neon Glass aesthetics.

    ❖ TESSERACT ENGINE ONLINE ❖
"""

import asyncio
import time
import sys
import logging
import random
import psutil
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
from cli.theme import NEON_GLASS_THEME
from cli.avatar import TesseractAvatar
from cli.layout import (
    make_layout,
    make_header,
    make_command_deck,
    make_sidebar_panel,
    make_log_panel,
)
from cli.raw_input import RawInputHandler, InputEvent, InputEventType
from cli.renderer import StreamingRenderer


# --- External integrations ---
try:
    from speak import GoogleHomeSpeaker, speak
except ImportError:
    class GoogleHomeSpeaker:
        def speak(self, text: str) -> None:
            time.sleep(len(text) * 0.05)
        def stop(self) -> None:
            pass
    
    def speak(text: str) -> None:
        time.sleep(len(text) * 0.05)

try:
    from brain import ask_brain
except ImportError:
    def ask_brain(prompt: str) -> str:
        time.sleep(1.5)
        return f"Neural response to: {prompt}"


# --- Configuration ---
@dataclass
class AppConfig:
    """Application configuration."""
    fps: int = 25 # High FPS for smooth 3D rotation
    model_name: str = "Tesseract v4.0"
    output_device: str = "Google Home"
    max_history: int = 50
    stream_text: bool = True
    boot_sequence: bool = True


# --- Conversation History ---
@dataclass
class Message:
    """A conversation message."""
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)


# --- Main Application ---
class CLIApp:
    """The Core - Project Tesseract Terminal."""

    BOOT_FRAMES = [
        "❖ INITIALIZING TESSERACT ENGINE ❖",
        "❖ LOADING 4D GEOMETRY ❖",
        "❖ ESTABLISHING ORBITAL UPLINK ❖",
        "❖ NEURAL LINK OPERATIONAL ❖",
    ]

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        
        # Use Neon Glass theme
        self.console = Console(theme=NEON_GLASS_THEME, force_terminal=True)
        
        logging.basicConfig(
            filename="core.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)

        # Core components
        self.state = get_state_manager()
        self.avatar = TesseractAvatar(width=30, height=15)
        self.layout = make_layout()
        self.input_handler = RawInputHandler()
        self.current_input = ""
        self.renderer = StreamingRenderer()
        
        try:
            self.speaker = GoogleHomeSpeaker()
        except Exception:
            self.speaker = None

        # State
        self.running = True
        self.history: deque[Message] = deque(maxlen=self.config.max_history)
        self.response_queue: asyncio.Queue[str] = asyncio.Queue()
        self.current_response = ""
        self.show_prompt = True
        self.boot_complete = False

        self._frame_count = 0
        
        # Network tracking
        self._last_net_io = psutil.net_io_counters() if hasattr(psutil, 'net_io_counters') else None
        self._last_net_time = time.time()
        self._net_sent_speed = 0.0
        self._net_recv_speed = 0.0

    def run(self) -> None:
        """Main application entry point."""
        try:
            asyncio.run(self._async_main())
        except KeyboardInterrupt:
            self._shutdown()
        except Exception as e:
            self._shutdown()
            raise
        finally:
            self.input_handler.stop()
            try:
                self.console.show_cursor()
            except Exception:
                pass

    async def _async_main(self) -> None:
        await self._run_boot_sequence()
        await self._run_main_loop()

    async def _run_boot_sequence(self) -> None:
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

        self.console.clear()
        self.boot_complete = True

    async def _run_main_loop(self) -> None:
        refresh_rate = 1.0 / self.config.fps

        self.input_handler.start()

        try:
            with Live(
                self.layout,
                console=self.console,
                refresh_per_second=self.config.fps,
                screen=True,
                transient=True,
                vertical_overflow="visible",
            ) as live:
                last_frame = time.time()

                while self.running:
                    now = time.time()
                    delta = now - last_frame

                    if delta < refresh_rate:
                        await asyncio.sleep(refresh_rate - delta)

                    last_frame = time.time()
                    self._frame_count += 1

                    self._process_state()
                    self._process_input()
                    await self._process_responses()
                    self._update_layout() # Renders frame

                    live.refresh()
        finally:
            self.input_handler.stop()

    def _process_state(self) -> None:
        current = self.state.state

        if current == AppState.IDLE:
            self.input_handler.enable()
        elif current == AppState.ERROR:
            self.input_handler.enable()
            if self.state.duration > 5.0:
                self.state.force_state(AppState.IDLE)

    def _process_input(self) -> None:
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
                if self.state.state != AppState.IDLE:
                    if self.state.state == AppState.TALKING and self.speaker:
                        self.speaker.stop()
                    self.renderer.skip()
                    self.state.force_state(AppState.IDLE)
                    self.input_handler.clear_buffer()
                    self.current_input = ""
                else:
                    self.running = False
                    break
            elif event.type == InputEventType.TEXT:
                self.input_handler.clear_buffer()
                if self.state.state == AppState.ERROR:
                    self.state.force_state(AppState.IDLE)
                else:
                    asyncio.create_task(self._handle_user_input(event.text))
        
        self.current_input = self.input_handler.input_text

    async def _handle_user_input(self, text: str) -> None:
        self.history.append(Message(role='user', content=text))
        self.state.transition_to(AppState.THINKING)
        asyncio.create_task(self._brain_worker(text))

    async def _brain_worker(self, prompt: str) -> None:
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, ask_brain, prompt)
            await self.response_queue.put(response)
        except Exception as e:
            self.logger.error(f"Brain worker failed: {e}", exc_info=True)
            self.state.set_error(str(e))

    async def _process_responses(self) -> None:
        try:
            response = self.response_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        self.history.append(Message(role='ai', content=response))
        
        if self.config.stream_text:
            self.renderer.start_stream(response)
        
        self.state.transition_to(AppState.TALKING)
        asyncio.create_task(self._speak_worker(response))

    async def _speak_worker(self, text: str) -> None:
        try:
            loop = asyncio.get_running_loop()
            if self.speaker:
                await loop.run_in_executor(None, self.speaker.speak, text)
            else:
                await loop.run_in_executor(None, speak, text)
        except Exception as e:
             self.logger.error(f"Audio error: {e}", exc_info=True)
        finally:
            while not self.renderer.is_complete:
                await asyncio.sleep(0.1)
            self.state.force_state(AppState.IDLE)

    def _update_layout(self) -> None:
        state_name = self.state.state_name
        
        # --- 1. Top Bar: Orbital Feed ---
        now = time.time()
        time_delta = now - self._last_net_time
        if time_delta > 1.0:
            net_io = psutil.net_io_counters()
            if self._last_net_io:
                bytes_sent = net_io.bytes_sent - self._last_net_io.bytes_sent
                bytes_recv = net_io.bytes_recv - self._last_net_io.bytes_recv
                self._net_sent_speed = (bytes_sent / 1024 / 1024) / time_delta
                self._net_recv_speed = (bytes_recv / 1024 / 1024) / time_delta
            self._last_net_io = net_io
            self._last_net_time = now

        self.layout["header"].update(
            make_header(
                cpu=psutil.cpu_percent(),
                ram=psutil.virtual_memory().percent,
                net_sent=self._net_sent_speed,
                net_recv=self._net_recv_speed
            )
        )
        
        # --- 2. Sidebar: Tesseract Engine (Right side) ---
        avatar_text = self.avatar.render(state_name)
        self.layout["sidebar"].update(
             make_sidebar_panel(avatar_text, state_name)
        )
        
        # --- 3. Footer: Command Link ---
        if state_name == "THINKING":
            deck_state = "THINKING"
        elif state_name == "TALKING":
            deck_state = "TALKING"
        else:
            deck_state = "IDLE"

        show_cursor = (self._frame_count % 15 < 8) and (deck_state == "IDLE")

        self.layout["footer"].update(
            make_command_deck(
                current_input=self.current_input,
                cursor_pos=self.input_handler.cursor_position,
                show_cursor=show_cursor,
                prompt_state=deck_state
            )
        )
        
        # --- 4. Main Log: Decaying Data Feed ---
        self.layout["log"].update(
            make_log_panel(self._render_decaying_history())
        )

    def _render_decaying_history(self) -> Group:
        """Render conversation history with Decay Effect."""
        elements = []
        
        # We only show the last 8 messages to keep the "Feed" look clean
        visible_history = list(self.history)[-8:]
        total_msgs = len(visible_history)
        
        for i, msg in enumerate(visible_history):
            # Calculate decay level based on age (position in list)
            # Newest = low index (if reversed) or high index (if normal)
            # Here: index 0 = oldest visible, index N = newest
            
            age = total_msgs - 1 - i
            decay_level = min(age, 4)
            style = f"text.decay.{decay_level}"
            
            if msg.role == 'user':
                text = Text()
                text.append("❯ ", style="dim")
                text.append(msg.content, style="user_input")
                elements.append(text)
                elements.append(Text(" ")) 
                
            elif msg.role == 'ai':
                content = msg.content
                
                # Apply corruption to very old messages
                if decay_level >= 3:
                     content = self._corrupt_text(content, decay_level)

                # Use streaming text if last message
                is_last = msg is self.history[-1] if self.history else False
                if is_last and self.renderer.is_streaming:
                     content = self.renderer.current_text
                     content += "█"
                     style = "text.decay.0" # Current message is always fresh
                
                # Render with decay style
                t = Text(content, style=style)
                elements.append(t)
                elements.append(Text("────────────────", style="dim"))
                elements.append(Text(" "))
        
        if not elements:
            t = Text()
            t.append("\n\n")
            t.append("   AWAITING VECTOR INPUT...", style="dim")
            return Group(t)
            
        return Group(*elements)

    def _corrupt_text(self, text: str, level: int) -> str:
        """Randomly corrupt characters for decay effect."""
        # This is purely visual, performance might be a concern if text is huge
        # But we only do it for old messages
        
        # Deterministic corruption based on text hash to avoid localized flickering
        # unless we want flickering "digital rot"
        
        # Let's do flickering rot
        chars = list(text)
        corruption_chance = 0.05 * (level - 2) # Level 3 = 5%, Level 4 = 10%
        
        for i in range(len(chars)):
            if chars[i] != " " and random.random() < corruption_chance:
                chars[i] = random.choice([".", ",", ";", "0", "1", "x"])
                
        return "".join(chars)

    def _shutdown(self) -> None:
        self.running = False
        self.console.clear()
        self.console.print("UPLINK SEVERED", style="bold magenta")


# --- Backward Compatibility ---
def run_cli() -> None:
    app = CLIApp()
    app.run()

if __name__ == "__main__":
    run_cli()
