# MorphGAC-segmentation-GUI
Semi-automated segmentation GUI

This work provides a GUI for a Semi-automated segmentation.
By a mouse click position, a number of iterations and a preprocessing image parameters,
the MorphGAC algorithm [1] searches for the optimal object contour.

The GUI implementation enables to perform a Semi-automated segmentation in a simple manner,
created as part of this research [2] for ultrasound breast tumors segmentation.
The algorithm and its theoretical derivation are described in [1].

![image](https://user-images.githubusercontent.com/67235383/170678265-7e33ca89-02e5-4899-9241-aac73f1f00f6.png)


If you use this implementation please cite the following papers:

   [1] A Morphological Approach to Curvature-based Evolution of Curves and
       Surfaces, Pablo Márquez-Neila, Luis Baumela and Luis Álvarez. In IEEE
       Transactions on Pattern Analysis and Machine Intelligence (PAMI),
       2014, DOI 10.1109/TPAMI.2013.106

   [2] Barkat L, Freiman M, Azhari H. Image translation of Ultrasound to Pseudo
       Anatomical Display by CycleGAN. arXiv preprint arXiv:2202.08053. 2022 Feb 16.
