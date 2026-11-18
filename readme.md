# Crash Bandicoot Desktop Character (1998) — Windows 10/11 Remastered Edition

A modern, expanded recreation in **Python + PySide6** of the official *Crash Bandicoot 2: Cortex Strikes Back* desktop mascot, originally released in 1998 by MDR Software Ltd. for SCEE.

**Remastered & Modernized by [@Hitsuji_Shiroi](https://github.com/HitsujiShiroi) (2026)**

---

## Key Features

* **Classic 1998 Fidelity:** Includes the original animations (*Jiggle*, *Foot Stomp*, *Pelvic Thrust*, *Turn Around*, *Behind You*), classic behavior rules, and a **Reset 1998 Defaults** button (`1x` scale and free-floating physics).
* **Dual Jukebox (PS1 vs. N. Sane Trilogy):** Soundtrack edition switcher with live transport controls (`Play/Pause`, `Next`, `Previous`), continuous playback independent of dancing, floating *Toast* notifications on track changes, quick volume presets, and separate volume sliders for music and sound effects (SFX).
* **10 Built-in Languages + Community Support:** English, Spanish, Portuguese, French, German, Italian, Arabic (RTL), Simplified Chinese, Japanese, and Korean.
* **Clones Mode (Multi-Crash):** Spawn multiple Crash instances on your screen, synchronize their dances, or clear extra clones with a single click.
* **Modular Character Support (`characters/`):** Easily add custom character packs using folders and `character.json` configuration files.
* **Native Windows 10/11 Integration:**
  * Crisp HD/4K pixel scaling (`1x` to `4x`), opacity control, window-landing gravity physics, and position pinning.
  * Automatic detection of fullscreen and exclusive fullscreen games/apps (`SHQueryUserNotificationState`) with smart auto-hide and pause, or a *Force Always-On-Top* mode.
  * Global rescue hotkey **`Ctrl + Shift + C`** (disables *Ghost Mode*, unlocks position, and centers the character).
  * Single-instance protection (*Single Instance Lock*) and safe configuration storage in `%APPDATA%\CrashMascot1998\crash_config.json`.

---

## How to Use

### Option A: Portable Package (`.7z` for Windows 10/11)
1. Extract the entire contents of the `.7z` archive into a folder of your choice.
2. Double-click **`CrashBandicootDesktop1998.exe`**.
3. **Right-click on Crash** or on its **System Tray icon** (near the Windows clock) to open the menu, switch languages, control music playback, or spawn clones.
4. If Windows SmartScreen displays a prompt on the first launch, click **More info** → **Run anyway**.

### Option B: From Source Code (Python 3.10+)
1. Extract the source code archive or clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## Customization & Contributions

### Adding New Languages
1. Open the `assets/lang/` folder and duplicate **`TEMPLATE_lang.json`**.
2. Rename the new file using the standard language code (e.g., `ru.json` or `pl.json`).
3. Change `"_lang_name"` to the native name of the language and translate the text values while keeping placeholder tags like `{track}`, `{num}`, `{w}`, `{h}`, and `{count}` intact.
4. Restart the application—your language will automatically appear under **Options -> Language**.

### Adding New Characters
Create a new subfolder inside `characters/<CharacterName>/` containing:
* `sprites/frame_000.png` ... `frame_159.png`
* `audio/ps1/` and/or `audio/nsane/`
* `character.json` defining `"name"` and the `"animations"` frame ranges.

---

## License & Legal Disclaimer
Please refer to the **`LICENSE`** file included in this package for the MIT License covering the software engine and the intellectual property disclaimer regarding the original *Crash Bandicoot* assets.