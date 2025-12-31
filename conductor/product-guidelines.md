# Product Guidelines: The Core CLI

## Visual Identity (Retro-Futurism)
- **Style:** "Retro-Futurism" - emulate the high-tech feel of 80s sci-fi terminals, but modernized with the Solarized Light color palette.
- **Key Elements:**
  - Use box-drawing characters (`┌`, `─`, `┐`, `│`, etc.) for all panels and layouts.
  - Employ block-level ASCII art for the avatar to evoke a vintage CRT display.
  - Simulated "low-res" feel while maintaining perfect crispness of modern terminal fonts.

## Color Palette (Solarized Light)
- **Base Text:** `#657b83` (Slate)
- **Primary Accent (Avatar/Header):** `#268bd2` (Blue)
- **Secondary Accent (Activity/Mouth):** `#d33682` (Magenta)
- **Visualization (Waveform):** `#2aa198` (Cyan)
- **User/Warning:** `#cb4b16` (Orange)

## Tone & Messaging
- **Persona:** Professional, efficient, yet slightly futuristic.
- **Feedback:** Provide immediate visual confirmation for every action (e.g., "Thinking...", "Speaking...").
- **Clarity:** Ensure Markdown content in the log is formatted for maximum readability on a light background.

## UI Principles
- **Persistence:** The layout must remain stable. Use `rich.live` to update components in place rather than scrolling.
- **Fluidity:** Animations (Avatar blinking, Waveform moving) must continue even when the system is processing or speaking.
- **Hierarchy:** Clear distinction between the system status (Header/Footer), the AI's presence (Sidebar), and the interaction history (Main Panel).
