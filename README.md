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

## Setup from GitHub

### 1. Clone the repository

```bash
git clone https://github.com/Vikramsrini/Crowd_analysis.git
cd Crowd_analysis
```

### 2. Python environment

Use Python **3.10+** (3.11 or 3.12 is fine).

```bash
python3 -m venv venv
source venv/bin/activate          # Windows (cmd): venv\Scripts\activate.bat
                                  # Windows (PowerShell): venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Video input

Sample videos under `data/sample_videos/` are **not** tracked by Git (only `.gitkeep` is). The default config points at a local file:

- Put an MP4 in `data/sample_videos/` and set `source` in `config/default.yaml`, **or**
- Set `source: 0` in `config/default.yaml` for the default webcam, **or**
- Set `source` to an RTSP URL or another file path.

### 4. YOLO weights (`yolov8n.pt`)

`*.pt` files are gitignored. On first run, **Ultralytics** usually downloads `yolov8n.pt` when the model loads (needs network access). If download fails (e.g. SSL or offline), download the weights manually from [Ultralytics releases](https://github.com/ultralytics/assets/releases) and place `yolov8n.pt` in the project root (same folder as `main.py`), matching `model_path` in `config/default.yaml`.

### 5. MCNN / dashboard weights

`crowd_counting_best.pth` is included in the repo for density features and `src/app.py`. Keep it in the project root unless you change paths in code.

### 6. Run the app

Follow **AI Analysis Pipeline (CLI)** and **Web Dashboard** below. For the API server, run from the repo root with:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"   # Windows PowerShell: $env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python src/app.py
```

### 7. Tests (optional)

```bash
pip install pytest
pytest tests/ -v
```

**Note:** Large local dataset archives (e.g. under `archive/`) are not in Git. Training notebooks may expect you to obtain data separately.

---

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
