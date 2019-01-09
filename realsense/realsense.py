import numpy as np
import pyrealsense2 as rs


class RealSense:
    def __init__(self, filters=[]):
        """
        Connect to RealSense and initialize filters
        :param filters: [String, ...], default=[]: '' TODO list filters
        """
        self.pipe = rs.pipeline()
        cfg = rs.config()
        profile = self.pipe.start(cfg)
        # camera parameters
        self.depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

        # filters to apply to depth images
        self.filters = filters
        if 'align' in self.filters:
            self.align = rs.align(rs.stream.color)
        if 'decimation' in self.filters:
            self.decimation = rs.decimation_filter()
            self.decimation.set_option(rs.option.filter_magnitude, 4)
        if 'spatial' in self.filters:
            self.spatial = rs.spatial_filter()
            # self.spatial.set_option(rs.option.holes_fill, 3)
            self.spatial.set_option(rs.option.filter_magnitude, 5)
            self.spatial.set_option(rs.option.filter_smooth_alpha, 1)
            self.spatial.set_option(rs.option.filter_smooth_delta, 50)
        if 'temporal' in self.filters:
            # TODO
            self.temporal = rs.temporal_filter()
            self.temporal_iters = 3
        if 'hole_filling' in self.filters:
            self.hole_filling = rs.hole_filling_filter()
        if 'colorize' in self.filters:
            self.colorizer = rs.colorizer()

    def cap(self, type='rs'):
        """
        Capture an rgb and depth frame, apply filters and return as rs object or np array
        :param type: String, default='rs': return realsense datatype for images with 'rs' or convert to numpy with 'np'
        :return:
        """
        # get set of frames from camera
        frameset = self.pipe.wait_for_frames()

        # align color and depth frame
        if 'align' in self.filters:
            frameset = self.align.process(frameset)
        # separate color and depth frame
        color_frame = frameset.get_color_frame()
        depth_frame = frameset.get_depth_frame()

        # filter depth images
        if 'decimation' in self.filters:
            depth_frame = self.decimation.process(depth_frame)
        if 'spatial' in self.filters:
            depth_frame = self.spatial.process(depth_frame)
        if 'temporal' in self.filters:
            depth_frame = self.temporal.process(depth_frame)
        if 'hole_filling' in self.filters:
            depth_frame = self.hole_filling.process(depth_frame)

        depth_colorized = None
        if 'colorize' in self.filters:
            depth_colorized = self.colorizer.colorize(depth_frame)

        # return numpy arrays of images
        if type == 'rs':
            return color_frame, depth_frame, depth_colorized
        elif type == 'np':
            return np.asanyarray(color_frame.get_data()), np.asanyarray(depth_frame.get_data()), np.asanyarray(depth_colorized.get_data())
        else:
            return None, None

    def get_3d(self, depth_frame, pixels, intrinsics):
        # get depth image as numpy array
        try:
            depth_frame = np.asanyarray(depth_frame.get_data())
        except AttributeError:
            pass

        # get 3d coordinates for every pixel
        out = []
        for px in pixels:
            depth_value = depth_frame[px[0], px[1]]
            out.append(rs.rs2_deproject_pixel_to_point(intrinsics, px, depth_value * self.depth_scale))

        return out
