# MorphGAC-segmentation-GUI
Semi-automated segmentation GUI

This work provides a GUI for a Semi-automated segmentation.
By **a mouse click position**, **a number of iterations** and **a preprocessing image parameters**,
the MorphGAC algorithm [1] searches for the optimal object contour.

The GUI implementation enables to perform a Semi-automated segmentation in a simple manner,
created as part of a research including an ultrasound breast tumors segmentation [2].
The algorithm and its theoretical derivation are described in [1].

![image](https://user-images.githubusercontent.com/67235383/170678265-7e33ca89-02e5-4899-9241-aac73f1f00f6.png)


### Installation
To install the GUI dependencies:

```
conda env create -f environment.yml
```

You may need to adjust the **preprocessing image parameters** for your specific data (For the inverse gaussian gradient filter which displayed in the center): 
- **alpha**: Controls the steepness of the Gaussian filter.
- **sigma**: Standard deviation of the Gaussian filter.

According to the [scikit-image documentation](https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.inverse_gaussian_gradient)



### Citation
If you use this implementation please cite the following papers:

   [1] A Morphological Approach to Curvature-based Evolution of Curves and
       Surfaces, Pablo Márquez-Neila, Luis Baumela and Luis Álvarez. In IEEE
       Transactions on Pattern Analysis and Machine Intelligence (PAMI),
       2014, DOI 10.1109/TPAMI.2013.106

   [2] Barkat L, Freiman M, Azhari H. Image translation of Ultrasound to Pseudo
       Anatomical Display by CycleGAN. arXiv preprint arXiv:2202.08053. 2022 Feb 16.
