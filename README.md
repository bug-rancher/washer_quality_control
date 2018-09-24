# Washer Quality Control

## About
This is a simple application for checking are produced washers have a correct dimensions. By using a machine vision to control quality of products, you can easily test a 100% of production and eliminate human errors.

## Installation
This application needs no installation. Just download, extract, and run. On Linux you may need give this program a permissions to execute (chmod +x Washer Quality Control).

## Context
This application is a element of machine vision system. This system consist also a horizontal, white translucent measurement plane with back light and camera above the plane. Produced washers are placed on measurement plane. Back light provide a high contrast between washers and background. Camera takes pictures of the scene, and then images are send to application.

## Problems during measurement
To provide a accurate results of measurement we need:
   * correct distortion (result of non ideal camera optic)
   * correct perspective (result of non ideal placement of the camera)
   * ignore elements on image that are not a washers (e.g. piece of background outside a lighted plane)

## How it works
1. First step in measurement process is a calibrate a camera. We need to take few pictures (minimum 10 with correct recognized corners by application) of special calibration chessboard in different positions to be able to calculate and correct a distortion. Also we need a one picture of chessboard lying down directly on measurement plane to wrap perspective.
2. We input images on first tab of the program, input parameters of chessboard and click "calculate". Program will find a internal corners of the chessboard and based on this calculate how much distorted are images and angled are measurement plane, and calculate coefficients to correct them.
3. We input images of washers that dimensions we know on second tab of the program and adjust threshold to get a correct value on image.
4. We input a upper and lower limits of internal end external diameters of the washers.
5. After adjusting we can measure other washers.

## Extras
1. Program comes with set of default images. If you use it first time, just click "calibrate" without change anything, and you will see how all should works.
2. Program make calculations with two methods:
   * processing only contours
   * processing whole image
3. Results of this two methods are displayed side by side, to provide a possibility of compare them.
   * Results of processing pure contours are placed on source, raw image.
   * Results of processing whole image are placed on undistorted image with corrected perspective.
   * Times of executing both methods are displayed on right side.
4. Results of the measurement are presented by draw a circles on detected edges and write a measured values. Values inside the limits are correct and will be draw with green color, and values outside the limits are incorrect and will be draw with red color.

## Screens
After start:
![screen 01](https://user-images.githubusercontent.com/42303256/45972393-e016e380-c03b-11e8-9e90-85d669868b0e.png)

Correction results:
![screen 02](https://user-images.githubusercontent.com/42303256/45972395-e016e380-c03b-11e8-9245-7b5159e5007a.png)

Measurement results:
![screen 03](https://user-images.githubusercontent.com/42303256/45972396-e0af7a00-c03b-11e8-9577-1fd25cee2c1e.png)

Bigger preview of results:
![screen 04](https://user-images.githubusercontent.com/42303256/45972397-e0af7a00-c03b-11e8-86b4-2263aeefd08f.png)
