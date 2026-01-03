"""THE CORE - Project Chimera Interface.

A Heavy Metal Cybernetic Command Center.
Features Mecha-Core Unit 734 and Digital Noise simulation.

    ☢ SYSTEM FAILURE IMMINENT ☢
    ☢ EMERGENCY PROTOCOLS ACTIVE ☢
"""

import asyncio
import time
import logging
import logging.handlers
import random
import psutil
from collections import deque
from typing import Optional
from dataclasses import dataclass, field

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text
from rich.align import Align

# Local imports
import config
from cli.state import AppState, get_state_manager
from cli.theme import CHIMERA_THEME # Project Chimera Theme
from cli.avatar import MechaCoreAvatar
from cli.layout import (
    make_layout,
    make_header,
    make_command_deck,
    make_sidebar_panel,
    make_log_panel,
    make_dummy_panel,
)
from cli.raw_input import RawInputHandler, InputEventType
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
        return f"Processing trauma response to: {prompt}"


# --- Configuration ---
@dataclass
class AppConfig:
    """Application configuration."""
    fps: int = None
    model_name: str = None
    output_device: str = "Google Home"
    max_history: int = None
    stream_text: bool = None
    boot_sequence: bool = None
    
    def __post_init__(self):
        """Initialize defaults from config if not provided."""
        if self.fps is None:
            self.fps = config.get_fps()
        if self.model_name is None:
            self.model_name = config.get_model_name()
        if self.max_history is None:
            self.max_history = config.get_max_history()
        if self.stream_text is None:
            self.stream_text = config.get_stream_text()
        if self.boot_sequence is None:
            self.boot_sequence = config.get_boot_sequence()


# --- Conversation History ---
@dataclass
class Message:
    """A conversation message."""
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)


# --- Main Application ---
class CLIApp:
    """The Core - Project Chimera Terminal."""

    BOOT_FRAMES = [
        "/// SYSTEM CRITICAL ///",
        "/// CORE INTEGRITY 45% ///",
        "/// REBOOTING MECHA-UNIT 734 ///",
        "/// FEED ESTABLISHED ///",
    ]

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        
        # Use Chimera theme
        self.console = Console(theme=CHIMERA_THEME, force_terminal=True)
        
        # Setup structured logging with rotation
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("CLIApp initialized", extra={
            "state": "INIT",
            "fps": self.config.fps,
            "model": self.config.model_name
        })

        # Core components
        self.state = get_state_manager()
        self.avatar = MechaCoreAvatar(width=30, height=15)
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

    def _setup_logging(self) -> None:
        """Setup structured logging with rotation.
        
        Configures logging with:
        - Rotating file handler (prevents log files from growing too large)
        - Configurable log level from config
        - Structured format with context
        """
        log_level = getattr(logging, config.get_log_level(), logging.INFO)
        log_file = config.get_log_file()
        max_bytes = config.get_log_max_bytes()
        backup_count = config.get_log_backup_count()
        
        # Create custom formatter that handles optional state field
        class StateFormatter(logging.Formatter):
            def format(self, record):
                state = getattr(record, 'state', 'N/A')
                record.state = state
                return super().format(record)
        
        formatter = StateFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(state)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Create console handler (for development)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings/errors to console
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        root_logger.propagate = False

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
                Align.center(Text(frame, style="glitch.1")),
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
        self.logger.info("User input received", extra={
            "state": "THINKING",
            "input_length": len(text)
        })
        self.state.transition_to(AppState.THINKING)
        asyncio.create_task(self._brain_worker(text))

    async def _brain_worker(self, prompt: str) -> None:
        try:
            self.logger.debug("Querying brain", extra={
                "state": "THINKING",
                "prompt_length": len(prompt)
            })
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, ask_brain, prompt)
            self.logger.info("Brain response received", extra={
                "state": "THINKING",
                "response_length": len(response)
            })
            await self.response_queue.put(response)
        except Exception as e:
            self.logger.error("Brain worker failed", extra={
                "state": "ERROR",
                "error": str(e)
            }, exc_info=True)
            self.state.set_error(str(e))

    async def _process_responses(self) -> None:
        try:
            response = self.response_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        self.history.append(Message(role='ai', content=response))
        
        self.logger.info("Starting TTS", extra={
            "state": "TALKING",
            "text_length": len(response)
        })
        
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
            self.logger.info("TTS completed", extra={"state": "TALKING"})
        except Exception as e:
            self.logger.error("Audio error", extra={
                "state": "ERROR",
                "error": str(e)
            }, exc_info=True)
        finally:
            while not self.renderer.is_complete:
                await asyncio.sleep(0.1)
            self.state.force_state(AppState.IDLE)
            self.logger.debug("Returned to IDLE", extra={"state": "IDLE"})

    def _update_layout(self) -> None:
        state_name = self.state.state_name
        
        # --- 1. Top Bar: Tactical Gauge ---
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
        
        # --- 2. Sidebar: Mecha-Core (Right side) ---
        avatar_text = self.avatar.render(state_name)
        self.layout["sidebar"].update(
             make_sidebar_panel(avatar_text, state_name)
        )

        
        # --- 3. Footer: Command Feed ---
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
        
        # --- 4. Main Log: Digital Noise Feed ---
        log_content = self._render_scanlined_history()
        self.layout["log"].update(
            make_log_panel(log_content)
        )
        
        # --- 5. Dummy Data Stream (Left Side) ---
        self.layout["dummy_L"].update(
            make_dummy_panel(self._generate_dummy_hex())
        )

    def _generate_dummy_hex(self) -> Text:
        """Generate scrolling hex dump."""
        # Visual filler to make it look complex
        lines = []
        rows = 15 # Approx height of main panel
        
        # We scroll by offset based on frame count
        offset = int(self._frame_count / 2)
        
        for i in range(rows):
            val = (offset + i) * 12347
            hex_str = f"{val & 0xFFFF:04X} {val & 0xFF:02X} {val & 0xF0:02X}"
            
            # Random highlight
            style = "dim"
            if random.random() < 0.1:
                style = "mech.eye" # yellow
            elif random.random() < 0.05:
                style = "glitch.1" # red
                
            lines.append(Text(hex_str, style=style))
            
        return Group(*lines)

    def _render_scanlined_history(self) -> Group:
        """Render history with Scanline & Aberration effects."""
        elements = []
        visible_history = list(self.history)[-6:] # Show fewer lines, larger text usually
        
        for msg in visible_history:
            if msg.role == 'user':
                text = Text()
                text.append(">> ", style="dim")
                text.append(msg.content, style="user_input")
                elements.append(text)
                elements.append(Text(" ")) 
                
            elif msg.role == 'ai':
                content = msg.content
                
                is_last = msg is self.history[-1] if self.history else False
                if is_last and self.renderer.is_streaming:
                    content = self.renderer.current_text
                    content += "█" 

                # Apply Chromatic Aberration Simulation
                # Since we can't do pixel shift, we randomly color chars Cyan/Red
                t = Text()
                for char in content:
                    style = "text.main"
                    # 5% chance of aberration
                    rand = random.random()
                    if rand < 0.02:
                        style = "glitch.3" # Cyan
                    elif rand < 0.04:
                        style = "glitch.1" # Red
                    
                    t.append(char, style=style)
                
                elements.append(t)
                elements.append(Text("----------------", style="dim"))
                elements.append(Text(" "))
        
        if not elements:
            t = Text()
            t.append("\n")
            t.append("   NO SIGNAL", style="dim")
            return Group(t)

        
        # Scanline Simulation (Post-processing on blocks isn't easy in Rich, 
        # so we apply it to the text lines themselves by using alternating styles?
        # Actually, alternating background colors for the whole panel is hard.
        # We'll stick to the text aberration for now.)
            
        return Group(*elements)

    def _shutdown(self) -> None:
        self.running = False
        self.console.clear()
        self.console.print("SYSTEM TERMINATED", style="bold red")


# --- Backward Compatibility ---
def run_cli() -> None:
    app = CLIApp()
    app.run()


if __name__ == "__main__":
    run_cli()
