# Research demonstration

`render.py` produces a 46-second silent 1920×1080 H.264 MP4, a compact animated README preview, a poster, and six storyboard frames. All text, coordinates, colors, motion timing and plotted data are editable in the script. No generated chart imagery or fabricated predictions are used.

Run `python scripts/demo/render.py` with Pillow and FFmpeg installed. On macOS the script uses Comic Sans MS and Times New Roman from `/System/Library/Fonts/Supplemental`; set `DEMO_FONT_DIR` to a directory containing those licensed fonts elsewhere. Font binaries are not redistributed.

Inputs: `site/assets/demo/evidence.json`, the two independent case PNGs, and the released example PNGs in `site/assets/`. Sources and protocol distinctions are in `site/assets/demo/transcript.html`. Captions are separately editable in `captions-en.vtt`. If timing/content changes, update the captions and transcript too.

The radar uses four selected LQA profiles from the paper; the website leaderboard is now synchronized with the same 25-model main table. Each number is a published rounded value. The English/Japanese comparison uses the same fixed English question and recorded run. It is illustrative, not a general language ranking.

The homepage embeds a user-controlled player with `preload="none"`. README uses a clickable animated preview because repository Markdown does not reliably embed relative MP4 players. Both link to the same full video.

The editable six-slide storyboard is `site/assets/demo/MInfoVisQA-demo-storyboard.pptx`. To rebuild it, run `storyboard.py`, then `build-storyboard.mjs` with the Artifact Tool runtime and `PRESENTATIONS_SKILL_DIR`/`RUNTIME_PYTHON` configured. The PPTX is a static editable storyboard; the MP4 motion timing lives in `render.py`.
