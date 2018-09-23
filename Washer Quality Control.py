
from tkinter import *

import Calibrator
import Meter
import GUI


default_gui_settings = {"number_of_squares_x": 20, "number_of_squares_y": 20, "square_length": 5.0,
                        "number_of_pixels_on_mm": 6, "decrease": 420, "translation_x": 300, "translation_y": 140,
                        "dimension_external_max": 19.4, "dimension_external_min": 18.0,
                        "dimension_internal_max": 6.6, "dimension_internal_min": 6.4, "threshold": 35}

default_images_distortion = ["/calibration/calib0.jpg", "/calibration/calib1.jpg", "/calibration/calib2.jpg",
                             "/calibration/calib3.jpg", "/calibration/calib4.jpg", "/calibration/calib5.jpg",
                             "/calibration/calib6.jpg", "/calibration/calib7.jpg", "/calibration/calib8.jpg",
                             "/calibration/calib9.jpg", "/calibration/calib10.jpg", "/calibration/calib11.jpg",
                             "/calibration/calib12.jpg", "/calibration/calib13.jpg"]

default_image_perspective = '/calibration/calib0.jpg'

default_images_measurement = ["/measurement/IMG_8537.jpg", "/measurement/m0.jpg", "/measurement/m1.jpg",
                              "/measurement/m2.jpg", "/measurement/m3.jpg", "/measurement/m4.jpg",
                              "/measurement/m5.jpg", "/measurement/m6.jpg", "/measurement/m7.jpg",
                              "/measurement/m8.jpg"]


class Application(Frame):

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()

        self.__create_application_modules()
        self.__connect_modules()
        self.__configure_gui()
        self.__configure_calibrator()
        self.__configure_meter()

    def __create_application_modules(self):

        self.calibrator = Calibrator.Calibrator()
        self.meter = Meter.Meter()
        self.gui = GUI.GUI()
        self.gui.grid()

    def __connect_modules(self):

        self.gui.connect_calibrator(self.calibrator)
        self.gui.connect_meter(self.meter)

        self.calibrator.connect_meter(self.meter)
        self.calibrator.connect_gui(self.gui)

        self.meter.connect_calibrator(self.calibrator)
        self.meter.connect_gui(self.gui)

    def __configure_gui(self):

        self.gui.create_widgets()
        self.gui.load_settings_default(default_gui_settings)
        self.gui.set_default_settings()
        self.gui.collect_settings()

    def __configure_calibrator(self):

        self.calibrator.load_paths_of_default_images_for_correction_distortion(default_images_distortion)
        self.calibrator.create_containers_images_distortion()
        self.calibrator.load_path_of_default_image_for_correction_perspective(default_image_perspective)
        self.calibrator.create_container_image_perspective()
        self.calibrator.reset()
        self.calibrator.display_information()
        self.calibrator.check_what_to_disable()

    def __configure_meter(self):

        self.meter.load_paths_of_default_images_for_measurement(default_images_measurement)
        self.meter.measure()
        self.meter.display_information()
        self.meter.check_what_to_disable()


# Create main window
root = Tk()

# Modify window
root.title("Quality control v1.0.0")
root.resizable(False, False)

# add a main frame
app = Application(root)
app.grid()

# start loop of events
root.mainloop()
