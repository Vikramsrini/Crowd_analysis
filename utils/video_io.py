"""Video I/O wrappers for capture and writing.

Abstracts OpenCV VideoCapture/VideoWriter to support file paths,
webcam indices, and RTSP URLs with a consistent interface.
"""

import cv2


class VideoSource:
    """Wraps cv2.VideoCapture for easy frame iteration.

    Attributes:
        source: Original source (file path, int, or URL).
        cap: Underlying OpenCV VideoCapture object.
    """

    def __init__(self, source, flip_code: int | None = None):
        """Open a video source.

        Args:
            source: File path (str), webcam index (int), or RTSP URL (str).
            flip_code: Optional flip code (0, 1, or -1).
        """
        # Convert string "0" to int 0 for webcam
        if isinstance(source, str) and source.isdigit():
            source = int(source)

        self.source = source
        self.flip_code = flip_code
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {source}")

    @property
    def fps(self) -> float:
        """Frames per second of the source."""
        return self.cap.get(cv2.CAP_PROP_FPS) or 30.0

    @property
    def frame_size(self) -> tuple[int, int]:
        """(width, height) of frames."""
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (w, h)

    def read(self):
        """Read the next frame.

        Returns:
            (success: bool, frame: np.ndarray | None)
        """
        ok, frame = self.cap.read()
        if ok and self.flip_code is not None:
            frame = cv2.flip(frame, self.flip_code)
        return ok, frame

    def __iter__(self):
        """Iterate over frames until the source is exhausted."""
        while True:
            ok, frame = self.read()
            if not ok:
                break
            yield frame

    def release(self):
        """Release the underlying capture."""
        self.cap.release()

    def __del__(self):
        self.release()


class VideoSink:
    """Wraps cv2.VideoWriter for saving annotated output.

    Attributes:
        path: Output file path.
        writer: Underlying OpenCV VideoWriter object.
    """

    def __init__(self, path: str, fps: float, frame_size: tuple[int, int]):
        """Create a video writer.

        Args:
            path: Output file path (e.g. "output.mp4").
            fps: Frames per second.
            frame_size: (width, height) of output frames.
        """
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.path = path
        self.writer = cv2.VideoWriter(path, fourcc, fps, frame_size)

        if not self.writer.isOpened():
            raise RuntimeError(f"Cannot open video writer: {path}")

    def write(self, frame):
        """Write a frame to the output video.

        Args:
            frame: BGR frame (np.ndarray).
        """
        self.writer.write(frame)

    def release(self):
        """Release the underlying writer."""
        self.writer.release()

    def __del__(self):
        self.release()
