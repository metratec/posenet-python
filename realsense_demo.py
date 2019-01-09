from realsense.realsense import RealSense
import cv2
import numpy as np
import tensorflow as tf


rs = RealSense(filters=['align', 'colorize', 'spatial', 'temporal', 'hole_filling'])

while True:
    color, depth, depth_colorized = rs.cap()
    # cv2.imshow('realsense', np.hstack((color, depth)))

    # get x, y, z of image point in meters
    color_intrin = color.profile.as_video_stream_profile().intrinsics
    points = rs.get_3d(np.asanyarray(depth.get_data()), [[240, 320]], color_intrin)
    print(points)

    color, depth_colorized = np.asanyarray(color.get_data()), np.asanyarray(depth_colorized.get_data())
    cv2.imshow('color', color)
    cv2.imshow('depth', depth_colorized)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
