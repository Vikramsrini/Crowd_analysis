# AI-Based Crowd Density Control & Abnormal Behavior Detection

Real-time person detection, crowd counting, tracking, and abnormal behavior detection using **YOLOv8**.

## Features

- **Person Detection** — YOLOv8 nano/small with configurable confidence
- **Multi-Object Tracking** — ByteTrack / BoT-SORT with persistent IDs
- **MCNN Density Estimation** — High-accuracy crowd counting with heatmaps (ShanghaiTech dataset)
- **ROI Crowd Counting** — Polygon zones with configurable thresholds
- **Abnormal Behavior Detection**:
  - Crowd surge (sudden count increase)
  - Panic / stampede (high average speed)
  - Loitering in restricted zones
  - Unauthorized entry detection
- **Web Dashboard** — React + Vite UI with live stream and historical analysis gallery
- **Alerts** — Console, sound, webhook, and JSONL file logging
- **Visualization** — Real-time bounding boxes, trails, ROI overlays, and alert banners

### 1. AI Analysis Pipeline (CLI)
The core real-time analysis pipeline with bounding boxes, tracks, and ROI overlays.
```bash
# Activate virtual environment
source venv/bin/activate

# Run the pipeline
python main.py
```
Press **q** to quit the visualization window.

---

### 2. Web Dashboard (Interactive)
The full web application with live stream analysis, historical statistics, and an MCNN density analysis gallery.

**Step A: Start the Backend (API)**
```bash
# In a new terminal tab
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python src/app.py
```

**Step B: Start the Frontend (UI)**
```bash
# In another terminal tab
cd dashboard
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

## Configuration

Edit `config/default.yaml` to tune:
- Detection model & confidence
- Video source (file / webcam / RTSP)
- ROI polygon definitions
- Behavior thresholds (surge, panic, loiter, intrusion)
- Alert channels

## Project Structure

```
├── config/default.yaml       # Configuration
├── src/
│   ├── detector.py           # YOLOv8 person detection
│   ├── tracker.py            # Multi-object tracking
│   ├── roi.py                # ROI management & counting
│   ├── behavior.py           # Abnormal behavior analysis
│   ├── alert.py              # Alert dispatching & logging
│   └── visualizer.py         # Frame annotation & display
├── utils/
│   ├── geometry.py           # Point-in-polygon, distance, IoU
│   ├── video_io.py           # Video capture/writer wrappers
│   └── logger.py             # Structured logging setup
├── tests/                    # Unit & integration tests
├── main.py                   # Pipeline entry point
└── requirements.txt          # Dependencies
```

## Testing

```bash
pip install pytest
pytest tests/ -v
```

## Requirements

- Python 3.10+
- Works on CPU or GPU (CUDA / MPS)
- All open-source dependencies
