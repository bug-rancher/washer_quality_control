
from threading import Thread
import copy
import os

import tkinter.filedialog
import numpy as np
import cv2 as cv

import ImageContainer


image_proportion = (3, 2)


class Calibrator(object):

    def __init__(self):

        self.__gui = None
        self.__meter = None

        self.__gui_settings = {}
        self.__information_actual = {}
        self.__calibration_results = {}

        iterations = 30
        accuracy = 0.1

        self.__termination_criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, iterations, accuracy)

        self.__points_on_chessboard = None

        self.__set_of_points_on_chessboard = None
        self.__set_of_points_on_image = None

        self.__paths_to_images_distortion = []
        self.__path_to_image_perspective = ""

        self.__camera_matrix = None
        self.__new_camera_matrix = None
        self.__distortion_coefficients = None
        self.__homography_matrix_for_measurement = None
        self.__homography_matrix_for_image = None

        self.__images_distortion = []
        self.__image_perspective = None

        self.__image_number = 0
        self.__number_of_images_ok = 0

    def connect_meter(self, meter):

        self.__meter = meter

    def connect_gui(self, gui):

        self.__gui = gui

    def load_paths_of_default_images_for_correction_distortion(self, paths_relative):

        for path in paths_relative:

            path_absolute = "".join((os.getcwd(), path))

            self.__paths_to_images_distortion.append(path_absolute)

    def load_path_of_default_image_for_correction_perspective(self, path_relative):

        path_absolute = "".join((os.getcwd(), path_relative))

        self.__path_to_image_perspective = path_absolute

    def create_containers_images_distortion(self):

        del self.__images_distortion[:]

        for i, path in enumerate(self.__paths_to_images_distortion):

            image = ImageContainer.ImageContainer()
            image.source = cv.imread(path)
            image.name = os.path.basename(path)
            image.number = i + 1

            image.with_corners = copy.deepcopy(image.source)

            self.__images_distortion.append(image)

    def create_container_image_perspective(self):

        self.__image_perspective = ImageContainer.ImageContainer()

        self.__image_perspective.source = cv.imread(self.__path_to_image_perspective)

    def reset(self):

        self.__points_on_chessboard = None

        self.__set_of_points_on_chessboard = None
        self.__set_of_points_on_image = None

        self.__camera_matrix = None
        self.__new_camera_matrix = None
        self.__distortion_coefficients = None
        self.__homography_matrix_for_measurement = None
        self.__homography_matrix_for_image = None

        for image in self.__images_distortion:

            image.with_corners = copy.deepcopy(image.source)

            image.is_correct = ""

        self.__image_perspective.no_distortion = None
        self.__image_perspective.no_distortion_no_perspective = None

        self.__image_number = 0
        self.__number_of_images_ok = 0

    def display_information(self):

        self.__collect_information()
        self.__gui.update_entries_calibration(self.__information_actual)

        if len(self.__images_distortion) > 0:

            self.__gui.display_image(self.__images_distortion[self.__image_number].with_corners,
                                     self.__gui.window_calibration_u_l)

        if self.__path_to_image_perspective is not "":

            self.__gui.display_image(self.__image_perspective.source, self.__gui.window_calibration_u_r)

    def check_what_to_disable(self):

        self.__disable_when_correction_not_calculated()
        self.__disable_when_no_images_for_distortion_correction()
        self.__disable_when_no_image_for_perspective_correction()
        self.__disable_until_correction_calculation_begin()
        self.__disable_when_no_images_for_any_correction()

    def __disable_when_correction_not_calculated(self):

        if (self.__new_camera_matrix is not None and self.__homography_matrix_for_measurement is not None
                and self.__homography_matrix_for_image is not None):

            pass

        else:

            self.__gui.remove_previews_images_after_correction()

    def __disable_when_no_images_for_distortion_correction(self):

        if len(self.__images_distortion) is 0:

            self.__gui.remove_preview_images_for_correction_distortion()
            self.__gui.disable_information_images_for_correction_distortion()
            self.__gui.disable_buttons_images_for_correction_distortion()

        else:

            self.__gui.enable_information_images_for_correction_distortion()
            self.__gui.enable_buttons_images_for_correction_distortion()

    def __disable_when_no_image_for_perspective_correction(self):

        if self.__path_to_image_perspective is "":

            self.__gui.remove_preview_image_for_correction_perspective()
            self.__gui.disable_information_image_for_correction_perspective()

        else:

            self.__gui.enable_information_image_for_correction_perspective()

    def __disable_until_correction_calculation_begin(self):

        if self.__points_on_chessboard is not None:

            self.__gui.enable_information_from_analysis_images_for_correction_distortion()

        else:

            self.__gui.disable_information_from_analysis_images_for_correction_distortion()

    def __disable_when_no_images_for_any_correction(self):

        if (len(self.__images_distortion) is 0) or (self.__path_to_image_perspective is ""):

            self.__gui.disable_button_calibration()

        else:

            self.__gui.enable_button_calibration()

    def run_calibration(self):

        thread_calibration = Thread(target=self.__calibrate)
        thread_calibration.start()

    def __calibrate(self):

        self.reset()
        self.__get_settings_from_gui()
        self.__create_points_on_chessboard()
        self.__gui.enable_information_from_analysis_images_for_correction_distortion()
        self.__create_correlated_sets_of_points()

        if self.__number_of_images_ok > 0:

            self.__calibrate_camera()
            self.__calculate_new_camera_matrix()
            self.__correct_distortion_on_image_perspective()
            self.__gui.display_image(self.__image_perspective.no_distortion, self.__gui.window_calibration_d_l)
            self.__calculate_homography_matrix_for_measurement()
            self.__calculate_homography_matrix_for_image()
            self.__correct_perspective_on_image_perspective()
            self.__gui.display_image(self.__image_perspective.no_distortion_no_perspective, self.__gui.window_calibration_d_r)
            self.__gui.enable_buttons_images_for_correction_distortion()
            self.__meter.measure()

    def __get_settings_from_gui(self):

        self.__gui_settings = self.__gui.get_settings()

    def __create_points_on_chessboard(self):

        self.__points_on_chessboard = []

        points_on_chessboard = []

        number_of_internal_corners_x = self.__gui_settings["number_of_squares_x"] - 1
        number_of_internal_corners_y = self.__gui_settings["number_of_squares_y"] - 1
        square_length = self.__gui_settings["square_length"]

        if number_of_internal_corners_x == number_of_internal_corners_y:

            for j in range(number_of_internal_corners_y):
                for i in range(number_of_internal_corners_x):
                    point_3d = [i * square_length, j * square_length, 0]

                    points_on_chessboard.append(point_3d)

        else:                                                                                                           # when chessboard shape is rectangle, findChessboardCorners detect corners in reverse order and without revert points on chessboard final image is reverted by 180 degrees

            for j in reversed(range(number_of_internal_corners_y)):
                for i in reversed(range(number_of_internal_corners_x)):
                    point_3d = [i * square_length, j * square_length, 0]

                    points_on_chessboard.append(point_3d)

        self.__points_on_chessboard = np.array(points_on_chessboard, np.float32)

    def __create_correlated_sets_of_points(self):

        self.__set_of_points_on_chessboard = []
        self.__set_of_points_on_image = []

        for image_number, image in enumerate(self.__images_distortion):

            image.gray = cv.cvtColor(image.source, cv.COLOR_BGR2GRAY)

            number_of_internal_corners_x = self.__gui_settings["number_of_squares_x"] - 1
            number_of_internal_corners_y = self.__gui_settings["number_of_squares_y"] - 1

            chessboard_size = (number_of_internal_corners_x, number_of_internal_corners_y)

            found, points_on_image = cv.findChessboardCorners(image.gray, chessboard_size, None)

            if found:

                self.__set_of_points_on_chessboard.append(self.__points_on_chessboard)
                self.__set_of_points_on_image.append(points_on_image)

                search_window_size = (5, 5)
                zero_zone = (-1, -1)

                corners_to_draw = cv.cornerSubPix(image.gray, points_on_image, search_window_size, zero_zone,
                                                  self.__termination_criteria)
                cv.drawChessboardCorners(image.with_corners, chessboard_size, corners_to_draw, found)

                image.is_correct = "yes"

                self.__number_of_images_ok += 1

            else:

                image.is_correct = "no"

            self.__image_number = image_number

            self.display_information()

            cv.waitKey(500)

    def __calibrate_camera(self):

        image_size = self.__images_distortion[0].gray.shape[::-1]

        _, self.__camera_matrix, self.__distortion_coefficients, _, _ = cv.calibrateCamera(
            self.__set_of_points_on_chessboard, self.__set_of_points_on_image, image_size, None, None)

    def __calculate_new_camera_matrix(self):

        image_size = self.__image_perspective.source.shape[1::-1]

        alpha = 1

        self.__new_camera_matrix, _ = cv.getOptimalNewCameraMatrix(self.__camera_matrix, self.__distortion_coefficients,
                                                                   image_size, alpha, image_size)

    def __correct_distortion_on_image_perspective(self):

        image_size = self.__image_perspective.source.shape[1::-1]

        map_x, map_y = cv.initUndistortRectifyMap(self.__camera_matrix, self.__distortion_coefficients, None,
                                                  self.__new_camera_matrix, image_size, cv.CV_32FC1)

        self.__image_perspective.no_distortion = cv.remap(self.__image_perspective.source, map_x, map_y, cv.INTER_LINEAR)

    def __calculate_homography_matrix_for_measurement(self):

        scale = 1
        translation_x = 0
        translation_y = 0

        self.__homography_matrix_for_measurement = self.__calculate_homography_matrix(scale, translation_x, translation_y)

    def __calculate_homography_matrix_for_image(self):

        scale = self.__gui_settings["number_of_pixels_on_mm"]
        translation_x = self.__gui_settings["translation_x"]
        translation_y = self.__gui_settings["translation_y"]

        self.__homography_matrix_for_image = self.__calculate_homography_matrix(scale, translation_x, translation_y)

    def __calculate_homography_matrix(self, scale, translation_x, translation_y):

        points_on_chessboard = []

        number_of_internal_corners_x = self.__gui_settings["number_of_squares_x"] - 1
        number_of_internal_corners_y = self.__gui_settings["number_of_squares_y"] - 1
        square_length = self.__gui_settings["square_length"]

        if number_of_internal_corners_x == number_of_internal_corners_y:

            for j in range(number_of_internal_corners_y):
                for i in range(number_of_internal_corners_x):
                    point_2d = [i * square_length * scale + translation_x,
                                j * square_length * scale + translation_y]

                    points_on_chessboard.append(point_2d)

        else:                                                                                                           # when chessboard shape is rectangle, findChessboardCorners detect corners in reverse order and without revert points on chessboard final image is reverted by 180 degrees

            for j in reversed(range(number_of_internal_corners_y)):
                for i in reversed(range(number_of_internal_corners_x)):
                    point_2d = [i * square_length * scale + translation_x,
                                j * square_length * scale + translation_y]

                    points_on_chessboard.append(point_2d)

        points_on_chessboard = np.array(points_on_chessboard, np.float32)

        self.__image_perspective.gray = cv.cvtColor(self.__image_perspective.no_distortion, cv.COLOR_BGR2GRAY)

        chessboard_size = (number_of_internal_corners_x, number_of_internal_corners_y)

        _, points_on_image = cv.findChessboardCorners(self.__image_perspective.gray, chessboard_size, None)

        homography_matrix, _ = cv.findHomography(points_on_image, points_on_chessboard, cv.LMEDS)

        return homography_matrix

    def __correct_perspective_on_image_perspective(self):

        decrease = self.__gui_settings["decrease"]

        image_size = (image_proportion[0] * decrease, image_proportion[1] * decrease)

        self.__image_perspective.no_distortion_no_perspective = cv.warpPerspective(
            self.__image_perspective.no_distortion, self.__homography_matrix_for_image, image_size)

    def update_image_after_corrections(self):

        self.__get_settings_from_gui()
        self.__calculate_homography_matrix_for_image()
        self.__correct_perspective_on_image_perspective()
        self.__gui.display_image(self.__image_perspective.no_distortion_no_perspective, self.__gui.window_calibration_d_r)

    def select_images_distortion(self):

        images = tkinter.filedialog.askopenfilenames()

        self.__paths_to_images_distortion = list(images)

        self.reset()
        self.create_containers_images_distortion()
        self.check_what_to_disable()
        self.display_information()

        self.__meter.get_calibration_results()
        self.__meter.check_what_to_disable()
        self.__meter.display_information()

    def select_image_perspective(self):

        image = tkinter.filedialog.askopenfilename()

        self.__path_to_image_perspective = image

        self.reset()
        self.create_container_image_perspective()
        self.check_what_to_disable()
        self.display_information()

        self.__meter.get_calibration_results()
        self.__meter.check_what_to_disable()
        self.__meter.display_information()

    def next_image(self):

        if self.__image_number < len(self.__images_distortion) - 1:
            self.__image_number += 1

            self.display_information()

    def previous_image(self):

        if self.__image_number > 0:
            self.__image_number -= 1

            self.display_information()

    def __collect_information(self):

        self.__information_actual.update({"number_of_images": len(self.__paths_to_images_distortion)})
        self.__information_actual.update({"number_of_images_ok": self.__number_of_images_ok})

        try:
            self.__information_actual.update({"image_number": self.__images_distortion[self.__image_number].number})
        except:
            self.__information_actual.update({"image_number": 0})

        try:
            self.__information_actual.update({"image_name": self.__images_distortion[self.__image_number].name})
        except:
            self.__information_actual.update({"image_name": ""})

        try:
            self.__information_actual.update({"image_is_correct": self.__images_distortion[self.__image_number].is_correct})
        except:
            self.__information_actual.update({"image_is_correct": ""})

        self.__information_actual.update({"perspective_image_name": os.path.basename(self.__path_to_image_perspective)})

    def __collect_results(self):

        self.__calibration_results.update({"distortion_coefficients": self.__distortion_coefficients})
        self.__calibration_results.update({"camera_matrix": self.__camera_matrix})
        self.__calibration_results.update({"new_camera_matrix": self.__new_camera_matrix})
        self.__calibration_results.update({"homography_matrix_image": self.__homography_matrix_for_image})
        self.__calibration_results.update({"homography_matrix_measurement": self.__homography_matrix_for_measurement})

    def get_results(self):

        self.__collect_results()

        return self.__calibration_results
