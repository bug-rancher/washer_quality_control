
class MeasureContainer(object):

    def __init__(self):

        self.image_source = None
        self.image_binary = None
        self.image_no_distortion = None
        self.image_no_distortion_no_perspective = None

        self.contours_source = None
        self.contours_no_distortion = []
        self.contours_no_distortion_no_perspective = []

        self.centres_source = []
        self.radiuses_source = []

        self.centres_no_distortion_no_perspective = []
        self.radiuses_no_distortion_no_perspective = []

        self.scale = 1
        self.image_for_results = None
        self.centres_for_results = []
        self.radiuses_for_results = []

        self.image_with_results = None

        self.measure_time = 0
