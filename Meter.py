
import datetime
import copy
import os

import tkinter.filedialog
import numpy as np
import cv2 as cv

import MeasureContainer


image_proportion = (3, 2)


class Meter(object):

    def __init__(self):

        self.__gui = None
        self.__calibrator = None

        self.__gui_settings = {}
        self.__information_actual = {}
        self.__calibration_results = {}

        self.__measure_contours = MeasureContainer.MeasureContainer()
        self.__measure_image = MeasureContainer.MeasureContainer()

        self.__paths_to_images_measurement = []

        self.__image_number = 0

    def connect_calibrator(self, calibrator):

        self.__calibrator = calibrator

    def connect_gui(self, gui):

        self.__gui = gui

    def load_paths_of_default_images_for_measurement(self, paths_relative):

        for path in paths_relative:

            path_absolute = "".join((os.getcwd(), path))

            self.__paths_to_images_measurement.append(path_absolute)

    def measure(self):

        self.__get_gui_settings()
        self.get_calibration_results()

        if len(self.__paths_to_images_measurement) is not 0:

            self.__load_image(self.__measure_contours)
            self.__load_image(self.__measure_image)

            self.__threshold_preview()

            if (self.__calibration_results["new_camera_matrix"] is not None
                    and self.__calibration_results["homography_matrix_measurement"] is not None
                    and self.__calibration_results["homography_matrix_image"] is not None):

                self.measure_with_processing_contours()
                self.measure_with_processing_image()

        self.check_what_to_disable()
        self.display_information()

    def __get_gui_settings(self):

        self.__gui_settings = self.__gui.get_settings()

    def get_calibration_results(self):

        self.__calibration_results = self.__calibrator.get_results()

    def __load_image(self, measure):

        measure.image_source = cv.imread(self.__paths_to_images_measurement[self.__image_number], 1)

    def __threshold_preview(self):

        threshold = self.__gui_settings["threshold"]

        self.__gui.display_image(self.__measure_contours.image_source, self.__gui.window_preview_u_l)
        self.__measure_contours.image_binary = self.__threshold_image(self.__measure_contours.image_source, threshold)
        self.__gui.display_image(self.__measure_contours.image_binary, self.__gui.window_preview_u_r)

    def __threshold_image(self, image, threshold):

        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        _, image_binary = cv.threshold(image_gray, threshold, 255, cv.THRESH_BINARY)

        return image_binary

    def measure_with_processing_contours(self):

        self.__get_gui_settings()
        self.get_calibration_results()

        threshold = self.__gui_settings["threshold"]

        beginning = datetime.datetime.now()

        self.__measure_contours.image_binary = self.__threshold_image(self.__measure_contours.image_source, threshold)
        self.__measure_contours.contours_source = self.__find_contours(self.__measure_contours.image_binary)
        self.__measure_contours.contours_no_distortion = self.__correct_distortion_contours(
            self.__measure_contours.contours_source)
        self.__measure_contours.contours_no_distortion_no_perspective = self.__correct_perspective_contours(
            self.__measure_contours.contours_no_distortion)
        self.__measure_contours.centres_no_distortion_no_perspective, \
            self.__measure_contours.radiuses_no_distortion_no_perspective = self.__calculate_centres_and_radiuses(
                self.__measure_contours.contours_no_distortion_no_perspective)
        self.__measure_contours.centres_source, self.__measure_contours.radiuses_source = \
            self.__calculate_centres_and_radiuses(self.__measure_contours.contours_source)
        self.__measure_contours.image_for_results = self.__measure_contours.image_source
        self.__measure_contours.radiuses_for_results = self.__measure_contours.radiuses_source
        self.__measure_contours.centres_for_results = self.__measure_contours.centres_source
        self.__draw_results(self.__measure_contours)

        end = datetime.datetime.now()

        self.__measure_contours.measure_time = (end - beginning).total_seconds()

        self.__gui.display_image(self.__measure_contours.image_source, self.__gui.window_preview_u_l)
        self.__gui.display_image(self.__measure_contours.image_binary, self.__gui.window_preview_u_r)
        self.__gui.display_image(self.__measure_contours.image_with_results, self.__gui.window_preview_d_l)
        self.__gui.display_image(self.__measure_contours.image_with_results, self.__gui.window_processing_contours)

    def measure_with_processing_image(self):

        self.__get_gui_settings()
        self.get_calibration_results()

        threshold = self.__gui_settings["threshold"]

        beginning = datetime.datetime.now()

        self.__measure_image.image_no_distortion = self.__correct_distortion_image(self.__measure_image.image_source)
        self.__measure_image.image_no_distortion_no_perspective = self.__correct_perspective_image(
            self.__measure_image.image_no_distortion)
        self.__measure_image.image_binary = self.__threshold_image(
            self.__measure_image.image_no_distortion_no_perspective, threshold)
        self.__measure_image.contours_no_distortion_no_perspective = self.__find_contours(
            self.__measure_image.image_binary)
        self.__measure_image.centres_no_distortion_no_perspective, \
            self.__measure_image.radiuses_no_distortion_no_perspective = self.__calculate_centres_and_radiuses(
                self.__measure_image.contours_no_distortion_no_perspective)
        self.__measure_image.scale = self.__gui_settings["number_of_pixels_on_mm"]
        self.__measure_image.image_for_results = self.__measure_image.image_no_distortion_no_perspective
        self.__measure_image.radiuses_for_results = self.__measure_image.radiuses_no_distortion_no_perspective
        self.__measure_image.centres_for_results = self.__measure_image.centres_no_distortion_no_perspective
        self.__draw_results(self.__measure_image)

        end = datetime.datetime.now()

        self.__measure_image.measure_time = (end - beginning).total_seconds()

        self.__gui.display_image(self.__measure_image.image_with_results, self.__gui.window_preview_d_r)
        self.__gui.display_image(self.__measure_image.image_with_results, self.__gui.window_processing_image)

    def __find_contours(self, image):

        _, contours, _ = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        return contours

    def __correct_distortion_contours(self, contours):

        contours_no_distortion = []

        for contour in contours:

            camera_matrix = self.__calibration_results["new_camera_matrix"]
            points_with_distortion = np.array(contour, dtype='float32')

            points_without_distortion = cv.undistortPoints(points_with_distortion, camera_matrix, None)

            points_homogeneous = cv.convertPointsToHomogeneous(points_without_distortion)

            rotation_vector = np.array([0, 0, 0], dtype='float32')
            translation_vector = np.array([0, 0, 0], dtype='float32')
            distortion_coefficients = self.__calibration_results["distortion_coefficients"]

            points_on_plane, _ = cv.projectPoints(points_homogeneous, rotation_vector, translation_vector, camera_matrix,
                                                  distortion_coefficients, points_without_distortion)

            contours_no_distortion.append(points_on_plane)

        return contours_no_distortion

    def __correct_perspective_contours(self, contours):

        contours_no_distortion_no_perspective = []

        for contour in contours:

            contour_points = []

            for point in contour:

                position_matrix = [[point.item(0, 0)], [point.item(0, 1)], [1]]

                position_matrix = np.array(position_matrix, np.float32)

                homography_matrix = self.__calibration_results["homography_matrix_measurement"]

                result_matrix = np.matmul(homography_matrix, position_matrix)

                x = result_matrix.item(0, 0) / result_matrix.item(2, 0)
                y = result_matrix.item(1, 0) / result_matrix.item(2, 0)

                point_without_perspective = [x, y]

                contour_points.append(point_without_perspective)

            contours_no_distortion_no_perspective.append(contour_points)

        return contours_no_distortion_no_perspective

    def __calculate_centres_and_radiuses(self, contours):

        centres = []
        radiuses = []

        for contour in contours:

            contour = np.array(contour, np.float32)

            centre, radius = cv.minEnclosingCircle(contour)

            centres.append(centre)
            radiuses.append(radius)

        return centres, radiuses

    def __draw_results(self, measure):

        measure.image_with_results = copy.deepcopy(measure.image_for_results)

        for contour_number in range(len(measure.centres_for_results)):

            measured_diameter = 2 * measure.radiuses_no_distortion_no_perspective[contour_number] / measure.scale

            if self.__in_range(measured_diameter):

                self.__distinguish_diameter(measure, contour_number, measured_diameter)

    def __in_range(self, diameter):

        dimension_ex_max = self.__gui_settings["dimension_external_max"]
        dimension_in_min = self.__gui_settings["dimension_internal_min"]

        maximum_deviation_in_percent = 10

        minimum = dimension_in_min - dimension_in_min * maximum_deviation_in_percent / 100
        maximum = dimension_ex_max + dimension_ex_max * maximum_deviation_in_percent / 100

        if minimum < diameter < maximum:
            return True

        else:
            return False

    def __distinguish_diameter(self, measure, contour_number, diameter):

        dimension_ex_min = self.__gui_settings["dimension_external_min"]
        dimension_in_max = self.__gui_settings["dimension_internal_max"]

        border = dimension_in_max + (dimension_ex_min - dimension_in_max) / 2

        if diameter > border:

            self.__draw_diameter_external(measure, contour_number, diameter)

        else:

            self.__draw_diameter_internal(measure, contour_number, diameter)

    def __draw_diameter_external(self, measure, contour_number, diameter):

        dimension_ex_max = self.__gui_settings["dimension_external_max"]
        dimension_ex_min = self.__gui_settings["dimension_external_min"]

        color_green = (0, 255, 0)
        color_red = (0, 0, 255)

        text_place = (40, -40)

        if dimension_ex_min < diameter < dimension_ex_max:

            self.__draw_diameter(measure, contour_number, diameter, text_place, color_green)

        else:

            self.__draw_diameter(measure, contour_number, diameter, text_place, color_red)

    def __draw_diameter_internal(self, measure, contour_number, diameter):

        dimension_in_max = self.__gui_settings["dimension_internal_max"]
        dimension_in_min = self.__gui_settings["dimension_internal_min"]

        color_green = (0, 255, 0)
        color_red = (0, 0, 255)

        text_translation = (20, 20)

        if dimension_in_min < diameter < dimension_in_max:

            self.__draw_diameter(measure, contour_number, diameter, text_translation, color_green)

        else:

            self.__draw_diameter(measure, contour_number, diameter, text_translation, color_red)

    def __draw_diameter(self, measure, contour_number, diameter, text_translation, color):

        centre = measure.centres_for_results[contour_number]
        radius = measure.radiuses_for_results[contour_number]

        centre = (int(centre[0]), int(centre[1]))
        radius = int(radius)

        cv.circle(measure.image_with_results, centre, radius, color)

        text_to_write = "".join(("{0:.3f}".format(diameter), " mm"))
        text_translation = (int(centre[0]) + text_translation[0], int(centre[1]) + text_translation[1])

        font = cv.FONT_HERSHEY_DUPLEX
        text_scale = 0.5

        cv.putText(measure.image_with_results, text_to_write, text_translation, font, text_scale, color)

    def __correct_distortion_image(self, image):

        camera_matrix = self.__calibration_results["camera_matrix"]
        distortion_coefficients = self.__calibration_results["distortion_coefficients"]
        new_camera_matrix = self.__calibration_results["new_camera_matrix"]

        image_size = image.shape[1::-1]

        map_x, map_y = cv.initUndistortRectifyMap(camera_matrix, distortion_coefficients, None, new_camera_matrix,
                                                  image_size, cv.CV_32FC1)

        image_no_distortion = cv.remap(image, map_x, map_y, cv.INTER_LINEAR)

        return image_no_distortion

    def __correct_perspective_image(self, image):

        decrease = self.__gui_settings["decrease"]

        image_size = (image_proportion[0] * decrease, image_proportion[1] * decrease)

        homography_matrix = self.__calibration_results["homography_matrix_image"]

        image_no_perspective = cv.warpPerspective(image, homography_matrix, image_size)

        return image_no_perspective

    def select_images_for_measurement(self):

        images = tkinter.filedialog.askopenfilenames()

        self.__paths_to_images_measurement = list(images)

        self.reset()
        self.check_what_to_disable()
        self.measure()

    def previous_image(self):

        if self.__image_number > 0:

            self.__image_number -= 1

        self.measure()

    def next_image(self):

        if self.__image_number < len(self.__paths_to_images_measurement) - 1:

            self.__image_number += 1

            self.measure()

    def reset(self):

        self.__image_number = 0

        self.__measure_contours = MeasureContainer.MeasureContainer()
        self.__measure_image = MeasureContainer.MeasureContainer()

    def display_information(self):

        self.collect_information()
        self.__gui.update_entries_measurement(self.__information_actual)

    def collect_information(self):

        self.__information_actual.update({"number_of_images": len(self.__paths_to_images_measurement)})
        self.__information_actual.update({"image_number": self.__image_number + 1})

        try:
            self.__information_actual.update({"image_name": os.path.basename(
                self.__paths_to_images_measurement[self.__image_number])})
        except:
            self.__information_actual.update({"image_name": ""})

        self.__information_actual.update(
            {"number_of_contours_contours": len(self.__measure_contours.contours_no_distortion_no_perspective)})
        self.__information_actual.update({"time_contours": self.__measure_contours.measure_time})
        self.__information_actual.update(
            {"number_of_contours_image": len(self.__measure_image.contours_no_distortion_no_perspective)})
        self.__information_actual.update({"time_image": self.__measure_image.measure_time})

    def check_what_to_disable(self):

        self.__disable_when_correction_not_calculated()
        self.__disable_when_no_images_for_measurement()

    def __disable_when_correction_not_calculated(self):

        if (self.__calibration_results["new_camera_matrix"] is not None
                and self.__calibration_results["homography_matrix_measurement"] is not None
                and self.__calibration_results["homography_matrix_image"] is not None):

            self.__gui.enable_results_processing_contours()
            self.__gui.enable_results_processing_image()

        else:

            self.__gui.remove_previews_image_after_processing_contours()
            self.__gui.remove_previews_image_after_processing_image()
            self.__gui.disable_results_processing_contours()
            self.__gui.disable_results_processing_image()

    def __disable_when_no_images_for_measurement(self):

        if len(self.__paths_to_images_measurement) is 0:

            self.__gui.remove_previews_images_to_measurement()
            self.__gui.remove_previews_image_after_processing_contours()
            self.__gui.remove_previews_image_after_processing_image()

            self.__gui.disable_results_processing_contours()
            self.__gui.disable_results_processing_image()

            self.__gui.disable_information_image_for_perspective()
            self.__gui.disable_buttons_images_for_measurement()

        else:

            self.__gui.enable_information_image_for_perspective()
            self.__gui.enable_buttons_images_for_measurement()
