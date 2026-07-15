# Fruit Slice AI

A webcam-controlled arcade fruit slicing game built with Python, OpenCV, MediaPipe, Pygame, and NumPy.

## Setup

```bash
python -m pip install -r requirements.txt
python main.py
```

## Browser version (GitHub Pages)

The repository root also contains a browser version in `index.html`. It uses
MediaPipe Web, requests the webcam only after the player chooses **Enable
camera & play**, and stores high scores in the browser. To publish it, push
the repository to GitHub and enable **Settings → Pages → Deploy from a branch
→ main → /(root)**. Open the GitHub Pages URL over HTTPS; webcam access does
not work from ordinary `file://` URLs.

The game includes hand-dwell menus, MediaPipe fingertip tracking, progressive fruit and bomb spawns, combo scoring, lives, pause and game-over screens, locally saved high scores, particle/juice bursts, a camera preview, FPS display, full-screen support, and generated sound effects/background ambience. No downloaded assets are required.

## Controls

Move your index fingertip over a button and hold it briefly to choose it. During play, swipe through fruit; avoid bombs. Hold over the PAUSE button in the top-right to pause. Keyboard and mouse are not used for gameplay.
