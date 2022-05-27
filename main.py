#!/usr/bin/env python
# coding: utf-8

""""
------------------------------------
  MorphGAC segmentation GUI
------------------------------------
This work provides a GUI for a Semi-automated segmentation.
By a mouse click position, a number of iterations and a preprocessing image parameters,
the MorphGAC algorithm [1] searches for the optimal object contour.

The GUI implementation enables to perform a Semi-automated segmentation in a simple manner,
created as part of a research including an ultrasound breast tumors segmentation [2].
The algorithm and its theoretical derivation are described in [1].

If you use this implementation please cite the following papers:

   [1] A Morphological Approach to Curvature-based Evolution of Curves and
       Surfaces, Pablo Márquez-Neila, Luis Baumela and Luis Álvarez. In IEEE
       Transactions on Pattern Analysis and Machine Intelligence (PAMI),
       2014, DOI 10.1109/TPAMI.2013.106

   [2] Barkat L, Freiman M, Azhari H. Image translation of Ultrasound to Pseudo
       Anatomical Display by CycleGAN. arXiv preprint arXiv:2202.08053. 2022 Feb 16.

"""


import os
import numpy as np
import cv2 as cv
import pandas as pd
import matplotlib
from matplotlib.widgets import TextBox, Button
from matplotlib import pyplot as plt
from skimage.segmentation import (morphological_geodesic_active_contour,
                                  inverse_gaussian_gradient,
                                  disk_level_set)

matplotlib.use('TkAgg')


class GUI:
    def __init__(self):
        self.mask = []
        self.igg_img = []
        self.pos = []
        self.iterations = []
        self.buttons = []
        self.iterator = 0
        self.image_name = ''
        self.img_path = ''
        self.close_flag = False
        self.callback = self.create_callback()

        self.fig = plt.figure(figsize=(12, 4.5))
        self.fig.canvas.manager.window.wm_geometry("+%d+%d" % (200, 200))
        self.axis = [self.fig.add_subplot(1, 3, i+1) for i in range(3)]

        # plus_button
        axbox_p_button = self.fig.add_axes([0.925, 0.55, 0.03, 0.07])
        self.plus_button = Button(axbox_p_button, "+")
        self.plus_button.on_clicked(self.plus)

        # iterations text_box
        axbox = plt.axes([0.925, 0.45, 0.03, 0.07])
        self.text_box = TextBox(axbox, '', initial='25')

        # minus_button
        axbox_m_button = self.fig.add_axes([0.925, 0.35, 0.03, 0.07])
        self.minus_button = Button(axbox_m_button, "-")
        self.minus_button.on_clicked(self.minus)

        # next_button
        axbox_next_button = self.fig.add_axes([0.55, 0.025, 0.03, 0.07])
        self.next_button = Button(axbox_next_button, ">")
        self.next_button.on_clicked(self.next_index)

        # reset_button
        axbox_reset_button = self.fig.add_axes([0.49, 0.025, 0.05, 0.07])
        self.reset_button = Button(axbox_reset_button, "reset")
        self.reset_button.on_clicked(self.reset)

        # back_button
        axbox_back_button = self.fig.add_axes([0.45, 0.025, 0.03, 0.07])
        self.back_button = Button(axbox_back_button, "<")
        self.back_button.on_clicked(self.back_index)

        # save
        axbox_save_button = self.fig.add_axes([0.74, 0.025, 0.05, 0.07])
        self.save_button = Button(axbox_save_button, "save")
        self.save_button.on_clicked(self.save)

        # close
        axbox_close_button = self.fig.add_axes([0.80, 0.025, 0.05, 0.07])
        self.close_button = Button(axbox_close_button, "close")
        self.close_button.on_clicked(self.close)

        # Read coordinates and iterations data into a DataFrame.
        try:
            self.df = pd.read_hdf('Coordinates.h5', 'df')
        except IOError:
            self.df = pd.DataFrame([], columns=['locations', 'iterations'])

    def plus(self, event):
        self.text_box.set_val(int(self.text_box.text) + 1)

    def minus(self, event):
        self.text_box.set_val(int(self.text_box.text) - 1)

    def next_index(self, event):
        self.buttons.append(1)
        return

    def back_index(self, event):
        self.buttons.append(-1)
        return

    def reset(self, event):
        self.buttons.append(0)
        return

    def save(self, event):
        mask_path = self.img_path.replace('.', '_mask.')
        matplotlib.image.imsave(mask_path, self.mask, cmap='Greys_r')

        self.df.loc[self.image_name, ["locations", "iterations"]] = [self.pos] + [self.iterations]
        self.df.to_hdf('Coordinates.h5', key='df', mode='w')
        self.buttons.append(1)
        return

    def close(self, event):
        self.buttons.append(0)
        self.close_flag = True
        plt.close()
        return

    def create_callback(self):
        def callback(level_set):
            """
            Update contour drawing on the two axes:
                Delete the previous displayed contour and present the updated contour.
            Create a combined mask according to the updated level set.
            An updating display of the iterations number as an indication of the algorithm progress.

            Parameters
            ----------
            level_set: ndarray
                binary mask of the image, initialized with a disk level set around the mouse click position.
                Iteratively changing during the morphological_geodesic_active_contour algorithm

            """
            if self.axis[0].collections:
                del self.axis[0].collections[0]
                del self.axis[1].collections[0]
            self.axis[0].contour(level_set, levels=[0.5], colors='red')
            self.axis[1].contour(level_set, levels=[0.5], colors='red')
            combined = (self.mask + level_set) > 0
            self.axis[2].images[0].set_data(combined)
            self.fig.canvas.draw()
            self.axis[1].set_title(self.iterator)
            self.iterator += 1
            plt.pause(0.0001)
        return callback

    def onclick(self, event):
        """
        If the mouse click position is inside the axes (not in the figure background and not inside the buttons):
            1. Save the mouse click position and the number of iterations.
            2. Initialize a disk level set around the mouse click position.
            3. Iterative extension of the contours on the Inverse Gaussian filtered image.
            4. Update the self.mask parameter with the generated mask.

        If there are more than one mouse click inside the axes, the generated masks are combined

        Parameters
        ----------
        event: button_press_event object

        """
        if event.inaxes is not None and not len(event.inaxes.texts):  # in axes and not in buttons
            self.pos.append(tuple([event.ydata, event.xdata]))  # save position coordinates
            self.iterations.append(int(self.text_box.text))  # save number of iterations

            if len(self.pos) >= 2:
                self.callback = self.create_callback()  # update callback for more than one segment
            self.iterator = 0

            init_level_set = disk_level_set(self.igg_img.shape, center=self.pos[-1], radius=5)
            new_mask = morphological_geodesic_active_contour(self.igg_img, iterations=self.iterations[-1],
                                                             init_level_set=init_level_set,
                                                             smoothing=1, threshold=0.7,
                                                             balloon=1, iter_callback=self.callback)
            self.mask = (new_mask + self.mask) > 0

    def one_image(self):
        """
        Adjust the GUI to a specific image:
            Display the image, the image apter applying Inverse Gaussian filter and an empty mask

            Apply onclick function for drawing the contours on the images according to the mouse click locations
            Wait for a button press, till pressing on back, next, reset, save or close button.

        """
        # Reset variables
        self.buttons = []
        self.iterations = []
        self.pos = []
        self.iterator = 0

        # Display the three axis without labels
        self.axis[1].set_title('')
        for i in range(3):
            self.axis[i].clear()
            plt.setp(self.axis[i].get_xticklabels(), visible=False)
            plt.setp(self.axis[i].get_yticklabels(), visible=False)
            self.axis[i].tick_params(axis='both', which='both', length=0)

        # Read image, apply Inverse Gaussian filter and initialize empty mask
        original_img = plt.imread(self.img_path)
        img = cv.imread(self.img_path)[..., 0] / 255.0
        self.igg_img = inverse_gaussian_gradient(img, alpha=100, sigma=1.5)
        self.mask = np.zeros_like(img)

        # Display the three images
        self.axis[0].imshow(original_img)
        self.axis[1].imshow(self.igg_img, cmap='Greys_r')
        self.axis[2].imshow(self.mask, vmin=0, vmax=1, cmap='Greys_r')

        # Wait for a button press, till pressing on back, next, reset, save or close
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        while not len(self.buttons):
            plt.waitforbuttonpress(timeout=0)
        return self.buttons[-1]

    def all_files(self, path):
        """
        Get a pre-segmented images path, sorting out the already generated masks,
        and apply 'one_image' function on the rest.

        'one_image' function returns an integer for updating the index:
            1  for the next image
            0  for re-segment the same image
           -1  for the previous image

        Parameters
        ----------
        path: string
            pre-segmented images path
        """

        for root, dirs, files in os.walk(path):
            sorted_files = [string for string in files if 'mask' not in string]
            index = 0
            while 0 <= index < len(sorted_files) and not self.close_flag:
                self.image_name = sorted_files[index]
                self.img_path = os.path.join(root, self.image_name)
                index += self.one_image()
            plt.close()


if __name__ == '__main__':
    gui = GUI()
    gui.all_files('pre_segmented_images')
    plt.show()
