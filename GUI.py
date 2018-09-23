
import tkinter.ttk as ttk
from tkinter import *
import PIL.ImageTk
import PIL.Image
import cv2 as cv


image_proportion = (3, 2)


class GUI(Frame):

    def __init__(self):
        super(GUI, self).__init__()

        self.__calibrator = None
        self.__meter = None

        self.__width_window_small = image_proportion[0] * 200
        self.__height_window_small = image_proportion[1] * 200
        self.__width_window_big = image_proportion[0] * 407
        self.__height_window_big = image_proportion[1] * 407

        self.__width_of_columns_when_spinboxes = (215, 95)
        self.__width_of_columns_when_entries = (200, 110)

        self.__background_color = self.cget('bg')

        self.__settings_default = {}
        self.__settings_actual = {}

    def connect_calibrator(self, calibrator):

        self.__calibrator = calibrator

    def connect_meter(self, meter):

        self.__meter = meter

    def create_widgets(self):

        self.__create_cards_main()
        self.__fill_cards_main()

    def __create_cards_main(self):

        self.__cards_main = ttk.Notebook(self)
        self.__cards_main.grid(padx=5, pady=5)

        self.__card_calibration = Frame(self)
        self.__card_measurement = Frame(self)

        self.__cards_main.add(self.__card_calibration, text="CALIBRATION")
        self.__cards_main.add(self.__card_measurement, text="MEASUREMENT")

    def __fill_cards_main(self):

        self.__fill_card_calibration()
        self.__fill_card_measurement()

    def __fill_card_calibration(self):

        self.__create_windows_calibration()
        self.__create_panel_calibration()

    def __create_windows_calibration(self):

        self.__label_frame_calibration_u_l = ttk.LabelFrame(self.__card_calibration,
                                                            text="images for distortion analysis")
        self.__label_frame_calibration_u_l.grid(row=0, column=0, padx=(11, 5), pady=(32, 5))

        self.__label_frame_calibration_u_r = ttk.LabelFrame(self.__card_calibration,
                                                            text="image for perspective analysis")
        self.__label_frame_calibration_u_r.grid(row=0, column=1, padx=(0, 5), pady=(32, 5))

        self.__label_frame_calibration_d_l = ttk.LabelFrame(self.__card_calibration,
                                                            text="measurement plane after distortion correction")
        self.__label_frame_calibration_d_l.grid(row=1, column=0, padx=(11, 5), pady=(0, 5))

        self.__label_frame_calibration_d_r = ttk.LabelFrame(self.__card_calibration,
                                                            text="measurement plane after distortion and perspective correction")
        self.__label_frame_calibration_d_r.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))

        self.window_calibration_u_l = Canvas(self.__label_frame_calibration_u_l, width=self.__width_window_small,
                                             height=self.__height_window_small)
        self.window_calibration_u_l.grid(padx=5, pady=5)

        self.window_calibration_u_r = Canvas(self.__label_frame_calibration_u_r, width=self.__width_window_small,
                                             height=self.__height_window_small)
        self.window_calibration_u_r.grid(padx=5, pady=5)

        self.window_calibration_d_l = Canvas(self.__label_frame_calibration_d_l, width=self.__width_window_small,
                                             height=self.__height_window_small)
        self.window_calibration_d_l.grid(padx=5, pady=5)

        self.window_calibration_d_r = Canvas(self.__label_frame_calibration_d_r, width=self.__width_window_small,
                                             height=self.__height_window_small)
        self.window_calibration_d_r.grid(padx=5, pady=5)

    def __create_panel_calibration(self):

        self.__frame_panel_calibration = Frame(self.__card_calibration)
        self.__frame_panel_calibration.grid(row=0, column=2, rowspan=2, padx=(6, 0), sticky=N)

        self.__create_settings_chessboard()
        self.__create_information_images_for_correction_distortion()
        self.__create_information_image_for_correction_perspective()
        self.__create_settings_image_after_correction()
        self.__create_button_calibration()

    def __create_settings_chessboard(self):

        self.__label_frame_chessboard = ttk.LabelFrame(self.__frame_panel_calibration, text="chessboard settings")
        self.__label_frame_chessboard.grid(row=0, padx=(0, 5), pady=(32, 10))
        self.__label_frame_chessboard.columnconfigure(index=0, minsize=self.__width_of_columns_when_spinboxes[0])
        self.__label_frame_chessboard.columnconfigure(index=1, minsize=self.__width_of_columns_when_spinboxes[1])

        self.__label_number_of_fields_x = Label(self.__label_frame_chessboard, text="number of fields on side x:")
        self.__label_number_of_fields_x.grid(row=0, column=0, padx=(10, 5), pady=(5, 0), sticky=W)

        self.__label_number_of_fields_y = Label(self.__label_frame_chessboard, text="number of fields on side y:")
        self.__label_number_of_fields_y.grid(row=1, column=0, padx=(10, 5), sticky=W)

        self.__label_square_length = Label(self.__label_frame_chessboard, text="length of square side [mm]:")
        self.__label_square_length.grid(row=2, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__spinbox_number_of_squares_x = Spinbox(self.__label_frame_chessboard, width=7, from_=2, to=999,
                                                     justify="right", command=self.__action_spinbox_chessboard)
        self.__spinbox_number_of_squares_x.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky=E)

        self.__spinbox_number_of_squares_y = Spinbox(self.__label_frame_chessboard, width=7, from_=2, to=999,
                                                     justify="right", command=self.__action_spinbox_chessboard)
        self.__spinbox_number_of_squares_y.grid(row=1, column=1, padx=(0, 5), sticky=E)

        self.__spinbox_square_length = Spinbox(self.__label_frame_chessboard, width=7, from_=0.1, to=999, increment=0.1,
                                               justify="right", command=self.__action_spinbox_chessboard)
        self.__spinbox_square_length.grid(row=2, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_information_images_for_correction_distortion(self):

        self.__label_frame_distortion = ttk.LabelFrame(self.__frame_panel_calibration,
                                                       text="images for distortion correction")
        self.__label_frame_distortion.grid(row=1, padx=(0, 5), pady=(0, 10))
        self.__label_frame_distortion.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_distortion.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__button_select_distortion = ttk.Button(self.__label_frame_distortion, text="select images", width=15,
                                                     command=self.__calibrator.select_images_distortion)
        self.__button_select_distortion.grid(row=0, columnspan=2, pady=10)

        self.__label_number_of_images_distortion = Label(self.__label_frame_distortion,
                                                         text="number of selected images:")
        self.__label_number_of_images_distortion.grid(row=1, column=0, padx=(10, 5), sticky=W)

        self.__label_number_of_images_ok_distortion = Label(self.__label_frame_distortion,
                                                            text="number of correct images:")
        self.__label_number_of_images_ok_distortion.grid(row=2, column=0, padx=(10, 5), sticky=W)

        self.__label_image_number_distortion = Label(self.__label_frame_distortion, text="image number:")
        self.__label_image_number_distortion.grid(row=3, column=0, padx=(10, 5), sticky=W)

        self.__label_image_name_distortion = Label(self.__label_frame_distortion, text="image name:")
        self.__label_image_name_distortion.grid(row=4, column=0, padx=(10, 5), sticky=W)

        self.__label_image_is_correct_distortion = Label(self.__label_frame_distortion, text="image is correct:")
        self.__label_image_is_correct_distortion.grid(row=5, column=0, padx=(10, 5), sticky=W)

        self.__entry_number_of_images_distortion = Entry(self.__label_frame_distortion, width=12, justify="center",
                                                         bg=self.__background_color)
        self.__entry_number_of_images_distortion.grid(row=1, column=1, padx=(0, 5), sticky=E)

        self.__entry_number_of_images_ok_distortion = Entry(self.__label_frame_distortion, width=12, justify="center",
                                                            bg=self.__background_color)
        self.__entry_number_of_images_ok_distortion.grid(row=2, column=1, padx=(0, 5), sticky=E)

        self.__entry_image_number_distortion = Entry(self.__label_frame_distortion, width=12, justify="center",
                                                     bg=self.__background_color)
        self.__entry_image_number_distortion.grid(row=3, column=1, padx=(0, 5), sticky=E)

        self.__entry_image_name_distortion = Entry(self.__label_frame_distortion, width=12, justify="center",
                                                   bg=self.__background_color)
        self.__entry_image_name_distortion.grid(row=4, column=1, padx=(0, 5), sticky=E)

        self.__entry_image_is_correct_distortion = Entry(self.__label_frame_distortion, width=12, justify="center",
                                                         bg=self.__background_color)
        self.__entry_image_is_correct_distortion.grid(row=5, column=1, padx=(0, 5), sticky=E)

        self.__frame_buttons_distortion = Frame(self.__label_frame_distortion)
        self.__frame_buttons_distortion.grid(row=6, column=0, columnspan=2)

        self.__button_previous_distortion = ttk.Button(self.__frame_buttons_distortion, text="<<", width=7,
                                                       command=self.__calibrator.previous_image)
        self.__button_previous_distortion.grid(row=0, column=0, padx=10, pady=10)

        self.__button_next_distortion = ttk.Button(self.__frame_buttons_distortion, text=">>", width=7,
                                                   command=self.__calibrator.next_image)
        self.__button_next_distortion.grid(row=0, column=1, padx=10, pady=10)

    def __create_information_image_for_correction_perspective(self):

        self.__label_frame_perspective = ttk.LabelFrame(self.__frame_panel_calibration,
                                                        text="image for perspective analysis")
        self.__label_frame_perspective.grid(row=2, padx=(0, 5), pady=(0, 10))
        self.__label_frame_perspective.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_perspective.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__button_select_perspective = ttk.Button(self.__label_frame_perspective, text="select image", width=15,
                                                      command=self.__calibrator.select_image_perspective)
        self.__button_select_perspective.grid(row=0, column=0, columnspan=2, pady=10)

        self.__label_image_name_perspective = Label(self.__label_frame_perspective, text="file name:")
        self.__label_image_name_perspective.grid(row=1, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__entry_image_name_perspective = Entry(self.__label_frame_perspective, width=12, justify="center",
                                                    bg=self.__background_color)
        self.__entry_image_name_perspective.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_settings_image_after_correction(self):

        self.__label_frame_after_correction = ttk.LabelFrame(self.__frame_panel_calibration,
                                                             text="customize image after correction")
        self.__label_frame_after_correction.grid(row=3, padx=(0, 5), pady=(0, 10))
        self.__label_frame_after_correction.columnconfigure(index=0, minsize=self.__width_of_columns_when_spinboxes[0])
        self.__label_frame_after_correction.columnconfigure(index=1, minsize=self.__width_of_columns_when_spinboxes[1])

        self.__label_number_of_pixels = Label(self.__label_frame_after_correction, text="number of pixels on mm:")
        self.__label_number_of_pixels.grid(row=0, column=0, padx=(10, 5), pady=(5, 0), sticky=W)

        self.__label_decrease = Label(self.__label_frame_after_correction, text="decrease:")
        self.__label_decrease.grid(row=1, column=0, padx=(10, 5), sticky=W)

        self.__label_translation_x = Label(self.__label_frame_after_correction, text="translation on x:")
        self.__label_translation_x.grid(row=2, column=0, padx=(10, 5), sticky=W)

        self.__label_translation_y = Label(self.__label_frame_after_correction, text="translation on y:")
        self.__label_translation_y.grid(row=3, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__spinbox_number_of_pixels = Spinbox(self.__label_frame_after_correction, width=7, from_=1, to=999,
                                                  justify="right", command=self.__action_spinbox_after_correction)
        self.__spinbox_number_of_pixels.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky=E)

        self.__spinbox_decrease = Spinbox(self.__label_frame_after_correction, width=7, from_=10, to=1000, increment=10,
                                          justify="right", command=self.__action_spinbox_after_correction)
        self.__spinbox_decrease.grid(row=1, column=1, padx=(0, 5), sticky=E)

        self.__spinbox_translation_x = Spinbox(self.__label_frame_after_correction, width=7, from_=10, to=1000, increment=10,
                                               justify="right",  command=self.__action_spinbox_after_correction)
        self.__spinbox_translation_x.grid(row=2, column=1, padx=(0, 5), sticky=E)

        self.__spinbox_translation_y = Spinbox(self.__label_frame_after_correction, width=7, from_=10, to=1000, increment=10,
                                               justify="right", command=self.__action_spinbox_after_correction)
        self.__spinbox_translation_y.grid(row=3, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_button_calibration(self):

        self.__button_calibration = ttk.Button(self.__frame_panel_calibration, text="CALIBRATION", width=15,
                                               command=self.__calibrator.run_calibration)
        self.__button_calibration.grid(row=10, padx=(0, 5))

    def __fill_card_measurement(self):

        self.__create_cards_on_card_measurement()
        self.__fill_cards_on_card_measurement()
        self.__create_panel_measurements()

    def __create_cards_on_card_measurement(self):

        self.__cards_on_card_measurement = ttk.Notebook(self.__card_measurement)
        self.__cards_on_card_measurement.grid(row=0, column=0, padx=5, pady=5)

        self.__card_preview = Frame(self)
        self.__card_processing_contours = Frame(self)
        self.__card_processing_image = Frame(self)

        self.__cards_on_card_measurement.add(self.__card_preview, text="preview")
        self.__cards_on_card_measurement.add(self.__card_processing_contours, text="contours processing")
        self.__cards_on_card_measurement.add(self.__card_processing_image, text="image processing")

    def __fill_cards_on_card_measurement(self):

        self.__fill_card_preview()
        self.__fill_card_processing_contours()
        self.__fill_card_processing_image()

    def __fill_card_preview(self):

        self.__label_frame_preview_u_l = ttk.LabelFrame(self.__card_preview, text="original image")
        self.__label_frame_preview_u_l.grid(row=0, column=0, padx=5, pady=5)

        self.__label_frame_preview_u_r = ttk.LabelFrame(self.__card_preview, text="binary image")
        self.__label_frame_preview_u_r.grid(row=0, column=1, padx=(0, 5), pady=5)

        self.__label_frame_preview_d_l = ttk.LabelFrame(self.__card_preview, text="results of contours processing")
        self.__label_frame_preview_d_l.grid(row=1, column=0, padx=5, pady=(0, 5))

        self.__label_frame_preview_d_r = ttk.LabelFrame(self.__card_preview, text="results of image processing")
        self.__label_frame_preview_d_r.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))

        self.window_preview_u_l = Canvas(self.__label_frame_preview_u_l, width=self.__width_window_small,
                                         height=self.__height_window_small)
        self.window_preview_u_l.grid(padx=5, pady=5)

        self.window_preview_u_r = Canvas(self.__label_frame_preview_u_r, width=self.__width_window_small,
                                         height=self.__height_window_small)
        self.window_preview_u_r.grid(padx=5, pady=5)

        self.window_preview_d_l = Canvas(self.__label_frame_preview_d_l, width=self.__width_window_small,
                                         height=self.__height_window_small)
        self.window_preview_d_l.grid(padx=5, pady=5)

        self.window_preview_d_r = Canvas(self.__label_frame_preview_d_r, width=self.__width_window_small,
                                         height=self.__height_window_small)
        self.window_preview_d_r.grid(padx=5, pady=5)

    def __fill_card_processing_contours(self):

        self.__label_frame_processing_contours = ttk.LabelFrame(self.__card_processing_contours,
                                                                text="results of contours processing")
        self.__label_frame_processing_contours.grid(padx=5, pady=5)

        self.window_processing_contours = Canvas(self.__label_frame_processing_contours, width=self.__width_window_big,
                                                 height=self.__height_window_big)
        self.window_processing_contours.grid(padx=5, pady=5)

    def __fill_card_processing_image(self):

        self.__label_frame_processing_image = ttk.LabelFrame(self.__card_processing_image,
                                                             text="results of image processing")
        self.__label_frame_processing_image.grid(padx=5, pady=5)

        self.window_processing_image = Canvas(self.__label_frame_processing_image, width=self.__width_window_big,
                                              height=self.__height_window_big)
        self.window_processing_image.grid(padx=5, pady=5)

    def __create_panel_measurements(self):

        self.__frame_panel_measurements = Frame(self.__card_measurement)
        self.__frame_panel_measurements.grid(row=0, column=1, sticky=N)

        self.__create_settings_threshold()
        self.__create_information_images_for_measurement()
        self.__create_settings_dimensions()
        self.__create_results_processing_contours()
        self.__create_results_processing_image()

    def __create_settings_threshold(self):

        self.__label_frame_threshold = ttk.LabelFrame(self.__frame_panel_measurements, text="threshold")
        self.__label_frame_threshold.grid(row=0, padx=(0, 5), pady=(32, 10))
        self.__label_frame_threshold.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_threshold.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__slider = ttk.Scale(self.__label_frame_threshold, from_=0, to=255, orient=HORIZONTAL, length=300)
        self.__slider.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.__slider.configure(command=lambda _: self.__action_slider())

        self.__label_threshold = Label(self.__label_frame_threshold, text="threshold value:")
        self.__label_threshold.grid(row=1, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__entry_threshold = Entry(self.__label_frame_threshold, width=12, justify="center", bg=self.__background_color)
        self.__entry_threshold.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_information_images_for_measurement(self):

        self.__label_frame_measurement = ttk.LabelFrame(self.__frame_panel_measurements, text="images for measurement")
        self.__label_frame_measurement.grid(row=1, padx=(0, 5), pady=(0, 10))
        self.__label_frame_measurement.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_measurement.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__button_select_measurement = ttk.Button(self.__label_frame_measurement, text="select images",
                                                      command=self.__meter.select_images_for_measurement, width=15)
        self.__button_select_measurement.grid(row=0, columnspan=2, pady=10)

        self.__label_number_of_images_measurement = Label(self.__label_frame_measurement, text="number of selected images:")
        self.__label_number_of_images_measurement.grid(row=1, column=0, padx=(10, 5), sticky=W)

        self.__label_image_number_measurement = Label(self.__label_frame_measurement, text="image number:")
        self.__label_image_number_measurement.grid(row=2, column=0, padx=(10, 5), sticky=W)

        self.__label_image_name_measurement = Label(self.__label_frame_measurement, text="image name:")
        self.__label_image_name_measurement.grid(row=3, column=0, padx=(10, 5), sticky=W)

        self.__entry_number_of_images_measurement = Entry(self.__label_frame_measurement, width=12, justify="center",
                                                          bg=self.__background_color)
        self.__entry_number_of_images_measurement.grid(row=1, column=1, padx=(0, 5), sticky=E)

        self.__entry_image_number_measurement = Entry(self.__label_frame_measurement, width=12, justify="center",
                                                      bg=self.__background_color)
        self.__entry_image_number_measurement.grid(row=2, column=1, padx=(0, 5), sticky=E)

        self.__entry_image_name_measurement = Entry(self.__label_frame_measurement, width=12, justify="center",
                                                    bg=self.__background_color)
        self.__entry_image_name_measurement.grid(row=3, column=1, padx=(0, 5), sticky=E)

        self.__frame_buttons_measurement = Frame(self.__label_frame_measurement)
        self.__frame_buttons_measurement.grid(row=10, columnspan=2)

        self.__button_previous_measurement = ttk.Button(self.__frame_buttons_measurement, text="<<", width=7,
                                                        command=self.__meter.previous_image)
        self.__button_previous_measurement.grid(row=0, column=0, padx=10, pady=10)

        self.__button_next_measurement = ttk.Button(self.__frame_buttons_measurement, text=">>", width=7,
                                                    command=self.__meter.next_image)
        self.__button_next_measurement.grid(row=0, column=1, padx=10, pady=10)

    def __create_settings_dimensions(self):

        self.__label_frame_dimensions = ttk.LabelFrame(self.__frame_panel_measurements, text="dimension limits")
        self.__label_frame_dimensions.grid(row=2, padx=(0, 5), pady=(0, 10))
        self.__label_frame_dimensions.columnconfigure(index=0, minsize=self.__width_of_columns_when_spinboxes[0])
        self.__label_frame_dimensions.columnconfigure(index=1, minsize=self.__width_of_columns_when_spinboxes[1])

        self.__label_dimension_ex_max = Label(self.__label_frame_dimensions, text="external dimension max [mm]:")
        self.__label_dimension_ex_max.grid(row=1, column=0, padx=(10, 5), pady=(5, 0), sticky=W)

        self.__label_dimension_ex_min = Label(self.__label_frame_dimensions, text="external dimension min [mm]:")
        self.__label_dimension_ex_min.grid(row=2, column=0, padx=(10, 5), sticky=W)

        self.__label_dimension_in_max = Label(self.__label_frame_dimensions, text="internal dimension max [mm]:")
        self.__label_dimension_in_max.grid(row=3, column=0, padx=(10, 5), sticky=W)

        self.__label_dimension_in_min = Label(self.__label_frame_dimensions, text="internal dimension min [mm]:")
        self.__label_dimension_in_min.grid(row=4, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__spinbox_dimension_ex_max = Spinbox(self.__label_frame_dimensions, width=7, from_=0.1, to=50,
                                                  justify="right", increment=0.1, command=self.__action_spinbox_dimension)
        self.__spinbox_dimension_ex_max.grid(row=1, column=1, padx=(0, 5), pady=(5, 0), sticky=E)

        self.__spinbox_dimension_ex_min = Spinbox(self.__label_frame_dimensions, width=7, from_=0.1, to=50,
                                                  justify="right", increment=0.1, command=self.__action_spinbox_dimension)
        self.__spinbox_dimension_ex_min.grid(row=2, column=1, padx=(0, 5), sticky=E)

        self.__spinbox_dimension_in_max = Spinbox(self.__label_frame_dimensions, width=7, from_=0.1, to=50,
                                                  justify="right", increment=0.1, command=self.__action_spinbox_dimension)
        self.__spinbox_dimension_in_max.grid(row=3, column=1, padx=(0, 5), sticky=E)

        self.__spinbox_dimension_in_min = Spinbox(self.__label_frame_dimensions, width=7, from_=0.1, to=50,
                                                  justify="right", increment=0.1, command=self.__action_spinbox_dimension)
        self.__spinbox_dimension_in_min.grid(row=4, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_results_processing_contours(self):

        self.__label_frame_results_contours = ttk.LabelFrame(self.__frame_panel_measurements, text="contours processing")
        self.__label_frame_results_contours.grid(row=3, padx=(0, 5), pady=(0, 10))
        self.__label_frame_results_contours.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_results_contours.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__label_number_of_contours_contours = Label(self.__label_frame_results_contours, text="number of contours:")
        self.__label_number_of_contours_contours.grid(row=0, column=0, padx=(10, 5), pady=(5, 0), sticky=W)

        self.__label_time_contours = Label(self.__label_frame_results_contours, text="measure time [s]:")
        self.__label_time_contours.grid(row=1, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__entry_number_of_contours_contours = Entry(self.__label_frame_results_contours, width=12, justify="center",
                                                         bg=self.__background_color)
        self.__entry_number_of_contours_contours.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky=E)

        self.__entry_time_contours = Entry(self.__label_frame_results_contours, width=12, justify="center",
                                           bg=self.__background_color)
        self.__entry_time_contours.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def __create_results_processing_image(self):

        self.__label_frame_results_image = ttk.LabelFrame(self.__frame_panel_measurements, text="image processing")
        self.__label_frame_results_image.grid(row=4, padx=(0, 5), pady=(0, 10))
        self.__label_frame_results_image.columnconfigure(index=0, minsize=self.__width_of_columns_when_entries[0])
        self.__label_frame_results_image.columnconfigure(index=1, minsize=self.__width_of_columns_when_entries[1])

        self.__label_number_of_contours_image = Label(self.__label_frame_results_image, text="number of contours:")
        self.__label_number_of_contours_image.grid(row=0, column=0, padx=(10, 5), pady=(5, 0), sticky=W)

        self.__label_time_image = Label(self.__label_frame_results_image, text="measure time [s]:")
        self.__label_time_image.grid(row=1, column=0, padx=(10, 5), pady=(0, 5), sticky=W)

        self.__entry_number_of_contours_image = Entry(self.__label_frame_results_image, width=12, justify="center",
                                                      bg=self.__background_color)
        self.__entry_number_of_contours_image.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky=E)

        self.__entry_time_image = Entry(self.__label_frame_results_image, width=12, justify="center",
                                        bg=self.__background_color)
        self.__entry_time_image.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky=E)

    def display_image(self, image, window):

        vector_length_gray = 2
        vector_length_color = 3

        image_vector_length = len(image.shape[:])

        if image_vector_length is vector_length_gray:

            self.__display_image(image, window)

        elif image_vector_length is vector_length_color:

            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            self.__display_image(image, window)

    def __display_image(self, image, window):

        image = PIL.Image.fromarray(image)

        window_width = int(window.cget("width"))
        window_height = int(window.cget("height"))

        ratio_x = image.width / window_width
        ratio_y = image.height / window_height

        ratio = max(ratio_x, ratio_y)

        width = int(image.width // ratio)
        height = int(image.height // ratio)

        image = image.resize((width, height), PIL.Image.ANTIALIAS)

        image = PIL.ImageTk.PhotoImage(image)

        window.image = image                                                                                            # keep reference to object - protect from garbage collector

        middle_point_x = window_width // 2
        middle_point_y = window_height // 2

        window.create_image(middle_point_x, middle_point_y, image=window.image)

    def load_settings_default(self, settings):

        self.__settings_default = settings

    def set_default_settings(self):

        self.__spinbox_number_of_squares_x.delete(0, "end")
        self.__spinbox_number_of_squares_x.insert(0, self.__settings_default["number_of_squares_x"])
        self.__spinbox_number_of_squares_y.delete(0, "end")
        self.__spinbox_number_of_squares_y.insert(0, self.__settings_default["number_of_squares_y"])
        self.__spinbox_square_length.delete(0, "end")
        self.__spinbox_square_length.insert(0, self.__settings_default["square_length"])

        self.__spinbox_number_of_pixels.delete(0, "end")
        self.__spinbox_number_of_pixels.insert(0, self.__settings_default["number_of_pixels_on_mm"])
        self.__spinbox_decrease.delete(0, "end")
        self.__spinbox_decrease.insert(0, self.__settings_default["decrease"])
        self.__spinbox_translation_x.delete(0, "end")
        self.__spinbox_translation_x.insert(0, self.__settings_default["translation_x"])
        self.__spinbox_translation_y.delete(0, "end")
        self.__spinbox_translation_y.insert(0, self.__settings_default["translation_y"])

        self.__spinbox_dimension_ex_max.delete(0, "end")
        self.__spinbox_dimension_ex_max.insert(0, self.__settings_default["dimension_external_max"])
        self.__spinbox_dimension_ex_min.delete(0, "end")
        self.__spinbox_dimension_ex_min.insert(0, self.__settings_default["dimension_external_min"])
        self.__spinbox_dimension_in_max.delete(0, "end")
        self.__spinbox_dimension_in_max.insert(0, self.__settings_default["dimension_internal_max"])
        self.__spinbox_dimension_in_min.delete(0, "end")
        self.__spinbox_dimension_in_min.insert(0, self.__settings_default["dimension_internal_min"])

        self.__slider.set(self.__settings_default["threshold"])
        self.__update_entry_threshold()

    def get_settings(self):

        self.collect_settings()

        return self.__settings_actual

    def collect_settings(self):

        self.__settings_actual.update({"number_of_squares_x": int(self.__spinbox_number_of_squares_x.get())})
        self.__settings_actual.update({"number_of_squares_y": int(self.__spinbox_number_of_squares_y.get())})
        self.__settings_actual.update({"square_length": float(self.__spinbox_square_length.get())})
        self.__settings_actual.update({"number_of_pixels_on_mm": int(self.__spinbox_number_of_pixels.get())})
        self.__settings_actual.update({"decrease": int(self.__spinbox_decrease.get())})
        self.__settings_actual.update({"translation_x": int(self.__spinbox_translation_x.get())})
        self.__settings_actual.update({"translation_y": int(self.__spinbox_translation_y.get())})
        self.__settings_actual.update({"dimension_external_max": float(self.__spinbox_dimension_ex_max.get())})
        self.__settings_actual.update({"dimension_external_min": float(self.__spinbox_dimension_ex_min.get())})
        self.__settings_actual.update({"dimension_internal_max": float(self.__spinbox_dimension_in_max.get())})
        self.__settings_actual.update({"dimension_internal_min": float(self.__spinbox_dimension_in_min.get())})
        self.__settings_actual.update({"threshold": int(self.__slider.get())})

    def __action_spinbox_chessboard(self):

        self.__check_spinboxes()

        self.__calibrator.reset()
        self.__calibrator.check_what_to_disable()
        self.__calibrator.display_information()

        self.__meter.reset()
        self.__meter.get_calibration_results()
        self.__meter.check_what_to_disable()
        self.__meter.display_information()

    def __action_spinbox_after_correction(self):

        self.__check_spinboxes()
        self.__update_windows_after_correction()

    def __action_spinbox_dimension(self):

        self.__check_spinboxes()
        self.__meter.measure()

    def __check_spinboxes(self):

        spinboxes_to_check = [self.__spinbox_number_of_squares_x, self.__spinbox_number_of_squares_y,
                              self.__spinbox_square_length, self.__spinbox_number_of_pixels, self.__spinbox_decrease,
                              self.__spinbox_translation_x, self.__spinbox_translation_y,
                              self.__spinbox_dimension_ex_max, self.__spinbox_dimension_ex_min,
                              self.__spinbox_dimension_in_max, self.__spinbox_dimension_in_min]

        for spinbox in spinboxes_to_check:

            input_value = spinbox.get()

            without_dot = input_value.replace(".", "", 1)

            if not without_dot.isdigit():
                spinbox.delete(0, "end")
                spinbox.insert(0, float(spinbox.cget("from")))

            elif float(input_value) < spinbox.cget("from"):
                spinbox.delete(0, "end")
                spinbox.insert(0, int(spinbox.cget("from")))

            elif float(input_value) > spinbox.cget("to"):
                spinbox.delete(0, "end")
                spinbox.insert(0, int(spinbox.cget("to")))

    def __update_windows_after_correction(self):

        self.__calibrator.update_image_after_corrections()
        self.__meter.measure_with_processing_image()

    def __action_slider(self):

        self.__meter.measure()
        self.__update_entry_threshold()

    def __update_entry_threshold(self):

        threshold = round(self.__slider.get())

        self.__entry_threshold.delete(0, "end")
        self.__entry_threshold.insert(0, threshold)

    def update_entries_calibration(self, calibration_settings):

        self.__entry_number_of_images_distortion.delete(0, "end")
        self.__entry_number_of_images_distortion.insert(0, calibration_settings["number_of_images"])
        self.__entry_number_of_images_ok_distortion.delete(0, "end")
        self.__entry_number_of_images_ok_distortion.insert(0, calibration_settings["number_of_images_ok"])
        self.__entry_image_number_distortion.delete(0, "end")
        self.__entry_image_number_distortion.insert(0, calibration_settings["image_number"])
        self.__entry_image_name_distortion.delete(0, "end")
        self.__entry_image_name_distortion.insert(0, calibration_settings["image_name"])
        self.__entry_image_is_correct_distortion.delete(0, "end")
        self.__entry_image_is_correct_distortion.insert(0, calibration_settings["image_is_correct"])

        self.__entry_image_name_perspective.delete(0, "end")
        self.__entry_image_name_perspective.insert(0, calibration_settings["perspective_image_name"])

    def update_entries_measurement(self, measurement_settings):

        self.__entry_number_of_images_measurement.delete(0, "end")
        self.__entry_number_of_images_measurement.insert(0, measurement_settings["number_of_images"])
        self.__entry_image_number_measurement.delete(0, "end")
        self.__entry_image_number_measurement.insert(0, measurement_settings["image_number"])
        self.__entry_image_name_measurement.delete(0, "end")
        self.__entry_image_name_measurement.insert(0, measurement_settings["image_name"])

        self.__entry_number_of_contours_contours.delete(0, "end")
        self.__entry_number_of_contours_contours.insert(0, measurement_settings["number_of_contours_contours"])
        self.__entry_time_contours.delete(0, "end")
        self.__entry_time_contours.insert(0, "{0:.6f}".format(measurement_settings["time_contours"]))
        self.__entry_number_of_contours_image.delete(0, "end")
        self.__entry_number_of_contours_image.insert(0, measurement_settings["number_of_contours_image"])
        self.__entry_time_image.delete(0, "end")
        self.__entry_time_image.insert(0, "{0:.6f}".format(measurement_settings["time_image"]))

    def remove_preview_images_for_correction_distortion(self):

        self.window_calibration_u_l.delete("all")

    def remove_preview_image_for_correction_perspective(self):

        self.window_calibration_u_r.delete("all")

    def remove_previews_images_after_correction(self):

        self.window_calibration_d_l.delete("all")
        self.window_calibration_d_r.delete("all")

    def remove_previews_images_to_measurement(self):

        self.window_preview_u_l.delete("all")
        self.window_preview_u_r.delete("all")

    def remove_previews_image_after_processing_contours(self):

        self.window_preview_d_l.delete("all")
        self.window_processing_contours.delete("all")

    def remove_previews_image_after_processing_image(self):

        self.window_preview_d_r.delete("all")
        self.window_processing_image.delete("all")

    def disable_information_images_for_correction_distortion(self):

        self.__label_image_number_distortion["state"] = DISABLED
        self.__label_image_name_distortion["state"] = DISABLED

        self.__entry_image_number_distortion.delete(0, "end")
        self.__entry_image_number_distortion["state"] = DISABLED
        self.__entry_image_name_distortion.delete(0, "end")
        self.__entry_image_name_distortion["state"] = DISABLED

    def enable_information_images_for_correction_distortion(self):

        self.__label_image_number_distortion["state"] = NORMAL
        self.__label_image_name_distortion["state"] = NORMAL

        self.__entry_image_number_distortion["state"] = NORMAL
        self.__entry_image_name_distortion["state"] = NORMAL

    def disable_information_from_analysis_images_for_correction_distortion(self):

        self.__label_number_of_images_ok_distortion["state"] = DISABLED
        self.__label_image_is_correct_distortion["state"] = DISABLED

        self.__entry_number_of_images_ok_distortion.delete(0, "end")
        self.__entry_number_of_images_ok_distortion["state"] = DISABLED
        self.__entry_image_is_correct_distortion.delete(0, "end")
        self.__entry_image_is_correct_distortion["state"] = DISABLED

    def enable_information_from_analysis_images_for_correction_distortion(self):

        self.__label_number_of_images_ok_distortion["state"] = NORMAL
        self.__label_image_is_correct_distortion["state"] = NORMAL

        self.__entry_number_of_images_ok_distortion["state"] = NORMAL
        self.__entry_image_is_correct_distortion["state"] = NORMAL

    def disable_buttons_images_for_correction_distortion(self):

        self.__button_previous_distortion["state"] = DISABLED
        self.__button_next_distortion["state"] = DISABLED

    def enable_buttons_images_for_correction_distortion(self):

        self.__button_previous_distortion["state"] = NORMAL
        self.__button_next_distortion["state"] = NORMAL

    def disable_information_image_for_correction_perspective(self):

        self.__label_image_name_perspective["state"] = DISABLED

        self.__entry_image_name_perspective.delete(0, "end")
        self.__entry_image_name_perspective["state"] = DISABLED

    def enable_information_image_for_correction_perspective(self):

        self.__label_image_name_perspective["state"] = NORMAL

        self.__entry_image_name_perspective["state"] = NORMAL

    def disable_button_calibration(self):

        self.__button_calibration["state"] = DISABLED

    def enable_button_calibration(self):

        self.__button_calibration["state"] = NORMAL

    def disable_results_processing_contours(self):

        self.__label_number_of_contours_contours["state"] = DISABLED
        self.__label_time_contours["state"] = DISABLED

        self.__entry_number_of_contours_contours.delete(0, "end")
        self.__entry_number_of_contours_contours["state"] = DISABLED
        self.__entry_time_contours.delete(0, "end")
        self.__entry_time_contours["state"] = DISABLED

    def enable_results_processing_contours(self):

        self.__label_number_of_contours_contours["state"] = NORMAL
        self.__label_time_contours["state"] = NORMAL

        self.__entry_number_of_contours_contours["state"] = NORMAL
        self.__entry_time_contours["state"] = NORMAL

    def disable_results_processing_image(self):

        self.__label_number_of_contours_image["state"] = DISABLED
        self.__label_time_image["state"] = DISABLED

        self.__entry_number_of_contours_image.delete(0, "end")
        self.__entry_number_of_contours_image["state"] = DISABLED
        self.__entry_time_image.delete(0, "end")
        self.__entry_time_image["state"] = DISABLED

    def enable_results_processing_image(self):

        self.__label_number_of_contours_image["state"] = NORMAL
        self.__label_time_image["state"] = NORMAL

        self.__entry_number_of_contours_image["state"] = NORMAL
        self.__entry_time_image["state"] = NORMAL

    def disable_information_image_for_perspective(self):

        self.__label_image_number_measurement["state"] = DISABLED
        self.__entry_image_number_measurement.delete(0, "end")
        self.__entry_image_number_measurement["state"] = DISABLED
        self.__label_image_name_measurement["state"] = DISABLED
        self.__entry_image_name_measurement.delete(0, "end")
        self.__entry_image_name_measurement["state"] = DISABLED

    def enable_information_image_for_perspective(self):

        self.__label_image_number_measurement["state"] = NORMAL
        self.__entry_image_number_measurement["state"] = NORMAL
        self.__label_image_name_measurement["state"] = NORMAL
        self.__entry_image_name_measurement["state"] = NORMAL

    def disable_buttons_images_for_measurement(self):

        self.__button_previous_measurement["state"] = DISABLED
        self.__button_next_measurement["state"] = DISABLED

    def enable_buttons_images_for_measurement(self):

        self.__button_previous_measurement["state"] = NORMAL
        self.__button_next_measurement["state"] = NORMAL
