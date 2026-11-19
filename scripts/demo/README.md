# Research demonstration

Run `python scripts/demo/render_short.py` with Pillow and FFmpeg installed to build the current 25-second, 1600×900 homepage video, poster and animated README preview. The paired chart images and recorded model responses are documented in `site/assets/demo/evidence.json`. The captions and transcript in the same directory follow the short film’s timing.

## Earlier 46-second version

The following scripts belong to the original six-scene version. Run them in a separate checkout when reproducing that version, since they use the same output paths.

`render.py` produces a 46-second silent 1920×1080 H.264 MP4, a compact animated README preview, a poster, and six storyboard frames. All text, coordinates, colors, motion timing and plotted data are editable in the script. No generated chart imagery or fabricated predictions are used.

Run `python scripts/demo/render.py` with Pillow and FFmpeg installed. On macOS the script uses Comic Sans MS and Times New Roman from `/System/Library/Fonts/Supplemental`; set `DEMO_FONT_DIR` to a directory containing those licensed fonts elsewhere. Font binaries are not redistributed.

Inputs: `site/assets/demo/evidence.json`, the two independent case PNGs, and the released example PNGs in `site/assets/`. Sources and protocol distinctions are in `site/assets/demo/transcript.html`. Captions are separately editable in `captions-en.vtt`. If timing/content changes, update the captions and transcript too.

The radar uses four selected LQA profiles from the paper; the paper reported 25 models. Each number is a published rounded value. The English/Japanese comparison uses the same fixed English question and recorded run. It is illustrative, not a general language ranking.

The homepage embeds a user-controlled player with `preload="none"`. README uses a clickable animated preview because repository Markdown does not reliably embed relative MP4 players. Both link to the same full video.

The editable six-slide storyboard is `site/assets/demo/MInfoVisQA-demo-storyboard.pptx`. To rebuild it, run `storyboard.py`, then `build-storyboard.mjs` with the Artifact Tool runtime and `PRESENTATIONS_SKILL_DIR`/`RUNTIME_PYTHON` configured. The PPTX is a static editable storyboard; the MP4 motion timing lives in `render.py`.
