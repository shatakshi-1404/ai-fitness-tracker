import numpy as np


def calculate_angle(a, b, c):
    """
    Calculate the angle at point b formed by points a-b-c.
    Returns angle in degrees (0-180).
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return round(angle, 1)


def get_landmark_coords(landmarks, index, frame_width, frame_height):
    """Extract pixel coordinates from a MediaPipe landmark."""
    lm = landmarks[index]
    return [int(lm.x * frame_width), int(lm.y * frame_height)]
