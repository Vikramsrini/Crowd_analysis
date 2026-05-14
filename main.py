"""Crowd Analysis Pipeline — Entry Point.

Orchestrates the full per-frame pipeline:
  Video → Detection → Tracking → ROI Counting → Behavior Analysis → Alerts → Visualization

Usage:
    python main.py                         # use config/default.yaml
    python main.py --config path/to.yaml   # use custom config
"""

import argparse
import sys

import cv2
import yaml

from src.behavior import BehaviorAnalyzer
from src.alert import AlertManager
from src.roi import ROIManager
from src.tracker import MultiTracker
from src.visualizer import Visualizer
from utils.logger import setup_logger
from utils.video_io import VideoSource, VideoSink

from ultralytics import YOLO


def load_config(path: str) -> dict:
    """Load YAML configuration file.

    Args:
        path: Path to the YAML config file.

    Returns:
        Configuration dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_crowd_thresholds(roi_configs: list[dict]) -> dict[str, int]:
    """Extract crowd thresholds from counting-type ROIs.

    Args:
        roi_configs: List of ROI config dicts.

    Returns:
        Dict mapping zone name -> threshold.
    """
    thresholds = {}
    for roi in roi_configs:
        if roi.get("type") == "counting" and "crowd_threshold" in roi:
            thresholds[roi["name"]] = roi["crowd_threshold"]
    return thresholds


def run(config_path: str):
    """Run the crowd analysis pipeline.

    Args:
        config_path: Path to the YAML configuration file.
    """
    # --- Load config ---
    cfg = load_config(config_path)
    logger = setup_logger(log_file=cfg.get("alert_log_file", "logs/events.jsonl"))
    logger.info(f"Loaded config from {config_path}")

    # --- Initialize components ---
    video = VideoSource(cfg["source"], flip_code=cfg.get("flip_code"))
    fps = video.fps
    logger.info(f"Video source: {cfg['source']} @ {fps:.1f} FPS, {video.frame_size}")

    # Shared YOLO model for detection + tracking
    model = YOLO(cfg.get("model_path", "yolov8n.pt"))

    tracker = MultiTracker(
        model=model,
        tracker_type=cfg.get("tracker", "bytetrack"),
        conf=cfg.get("confidence_threshold", 0.4),
        max_history=cfg.get("track_history_length", 90),
        device=cfg.get("device", "auto"),
    )

    roi_manager = ROIManager(cfg.get("rois", []))
    logger.info(f"Loaded {len(roi_manager.zones)} ROI zones")

    behavior = BehaviorAnalyzer(
        fps=fps,
        surge_delta=cfg.get("surge_delta", 10),
        surge_window_sec=cfg.get("surge_window_sec", 3.0),
        panic_speed_thresh=cfg.get("panic_speed_thresh", 200.0),
        panic_duration_frames=cfg.get("panic_duration_frames", 15),
        loiter_time_sec=cfg.get("loiter_time_sec", 30.0),
        intrusion_cooldown_sec=cfg.get("intrusion_cooldown_sec", 5.0),
    )

    alert_mgr = AlertManager(
        crowd_thresholds=build_crowd_thresholds(cfg.get("rois", [])),
        console_enabled=cfg.get("alert_console", True),
        sound_enabled=cfg.get("alert_sound", False),
        webhook_url=cfg.get("alert_webhook_url"),
        log_file=cfg.get("alert_log_file", "logs/events.jsonl"),
    )

    visualizer = Visualizer(display=cfg.get("display", True))

    # Optional output video
    sink = None
    if cfg.get("output_video"):
        sink = VideoSink(cfg["output_video"], fps, video.frame_size)

    # --- Main loop ---
    logger.info("Starting pipeline... Press 'q' to quit.")
    frame_count = 0

    try:
        for frame in video:
            frame_count += 1

            # Step 1 + 2: Detection & Tracking (combined in tracker.update)
            tracks = tracker.update(frame)

            # Step 3: ROI counting
            roi_counts = roi_manager.count(tracks)

            # Step 4: Behavior analysis
            events = behavior.analyze(tracks, roi_counts, roi_manager)

            # Step 5: Alerts
            alert_msgs = alert_mgr.process(roi_counts, events)

            # Step 6: Visualization
            annotated = visualizer.render(
                frame, tracks, roi_manager, roi_counts, alert_msgs
            )

            # Write to output video if configured
            if sink:
                sink.write(annotated)

            # Keyboard control
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                logger.info("User requested quit.")
                break

            # Periodic status log
            if frame_count % 100 == 0:
                total_count = sum(roi_counts.values())
                logger.info(
                    f"Frame {frame_count}: {len(tracks)} tracks, "
                    f"ROI total={total_count}"
                )

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        video.release()
        if sink:
            sink.release()
        visualizer.close()
        logger.info(f"Pipeline finished. Processed {frame_count} frames.")


def main():
    """Parse CLI arguments and launch the pipeline."""
    parser = argparse.ArgumentParser(
        description="AI-Based Crowd Density Control & Abnormal Behavior Detection"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/default.yaml",
        help="Path to YAML config file (default: config/default.yaml)",
    )
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
