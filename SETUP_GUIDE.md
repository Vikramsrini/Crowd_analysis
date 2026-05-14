# Setup Guide

I've set up the project environment for you:

1.  **Created Virtual Environment**: `venv/` is ready.
2.  **Installed Dependencies**: `requirements.txt` packages installed.
3.  **Downloaded Sample Video**: `data/sample_videos/crowd.mp4` (from Intel IoT samples).
4.  **Downloaded Model**: `yolov8n.pt` (manually downloaded to fix SSL issues).

## How to Run

```bash
# Activate the environment
source venv/bin/activate

# Run the project
python main.py
```

- When running, frame processing will start.
- Detections started appearing around frame 200 (2 tracks) in my verification.
- Press `q` to quit the visualization window.

## Troubleshooting

- If `cv2.imshow` fails (headless env), try setting `display: false` in `config/default.yaml` and enable `output_video: output.mp4` instead.
