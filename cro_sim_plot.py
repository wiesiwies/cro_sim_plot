#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    cro_sim_plot
    Copyright (C) 2023  Thomas Wiesner

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors

from numba import jit

import datetime

def hsv_bloom(h, x, bp=0.5):
    """
    Generate a HSV color list from black (x = 0) over H fully saturated
    (x = bp) to white (x = 1.0).

    Parameters
    ----------
    h : float
        HSV color hue.
    x : float
        Value to map to a color. Must be in the range [0, 1.0].
        May be a list or 1d array.
    bp : float
        "Breaking point". The output color os fully saturated at x = bp.
        Must be in the range [0, 1.0].

    Returns
    -------
    M : 2d numpy array.
        One HSV color per row. As many rows as entries in x.

    """
    # bp: "break"-point; Transition point from value-change to saturation-change
    
    M = np.zeros((len(x), 3))
    
    M[:,0] = h

    for idx,xv in enumerate(x):
        if xv < bp:
            #matplotlib.colors.hsv_to_rgb([h, 1, x/bp])
            M[idx,1] = 1
            M[idx,2] = xv/bp
        else:
            #matplotlib.colors.hsv_to_rgb([h, 1-(x-bp)/(1-bp), 1])
            M[idx,1] = 1-(xv-bp)/(1-bp)
            M[idx,2] = 1
    return M

def cmap_color_white(h, pwr, bp=0.5):
    """
    Generates a colormap ranging from black over the fully saturated color H
    (HSV hue) to white.

    Parameters
    ----------
    h : float
        HSV hue.
    pwr : float
        Exponent for the color mapping.
    bp : TYPE, optional
        bp of hsv_bloom().

    Returns
    -------
    matplotlib.colors.ListedColormap
        Generated colormap.

    """
    
    # Quite some entries are necessary to avoid color banding in some cases.
    N = 1024
    
    x = np.linspace(0, 1, N)**pwr
    
    hsv = hsv_bloom(h, x, bp=bp)
    rgb = matplotlib.colors.hsv_to_rgb(hsv)
    return matplotlib.colors.ListedColormap(rgb)


def psf(psfSz, decay=3):
    """
    Generates circular point spread function matrix for simulating the CRT
    beam in the form of
        intensity = exp(-(x**2 + y**2)*decay)
    where x and y are from the interval [-1, 1].

    Parameters
    ----------
    psfSz : int
        Size of the point spread function in pixels. Must be an odd number.
    decay : float, optional
        Spatial decay. The default is 3.

    Raises
    ------
    RuntimeError
        If the size if not odd.

    Returns
    -------
    psfZ : 2d numpy array
        The PSF

    """
    if psfSz % 2 == 0:
        raise RuntimeError('PSF size must be odd.')
    psfX = np.linspace(-1, 1, psfSz)
    
    xv, yv = np.meshgrid(psfX, psfX)
    psfZ = np.exp(-(xv**2 + yv**2)*decay)
    
    return psfZ


@jit(nopython=True)
def update_screen(lens, t, px, py, z, screen, pxHeight, pxWidth, PSF):
    """
        Helper function for crt_plot to allow for Numba acceleration.
    """
    
    psfSz = PSF.shape[0]

    # Iterate over all line segments
    for idx in range(px.size-1):
        steps = lens[idx]

        dt = t[idx+1] - t[idx]
    
        # Iterate over the line interpolation points    
        for step in range(steps):
            # Interpolate the values
            xx = int(px[idx] + (px[idx+1] - px[idx])*step/steps)
            yy = int(py[idx] + (py[idx+1] - py[idx])*step/steps)
            zz = z[idx] + (z[idx+1] - z[idx])*step/steps
            
            # Update screen matrix if the point is within the screen boundaries
            if xx >= 0 and yy >= 0 and yy < pxHeight and xx < pxWidth:
                screen[yy:yy+psfSz, xx:xx+psfSz] += dt/steps*PSF*zz
            
    return screen


def crt_plot(x, y, t, xRange, yRange, pxWidth, pxHeight=None, z=None,
            oversample_t=3, psfSz=9, psfDecay=3,
            cmap=cmap_color_white(0.45, 0.6, bp=0.8)):
    """
    Simulate the behavior of an oscilloscope CRT (cathode ray tube) screen
    by tracing the lines and integrating the beam exposure.
    
    Draws into the current axis of the current figure.
    
    Note: Can take quite some time to compute!

    Parameters
    ----------
    x : 1d array of floats
        x values
    y : 1d array of floats
        y values
    t : 1d array of floats
        Time values, when the corresponding (x,y) pair is reached.
    xRange : tuple of 2 floats
        Horizontal (x) min/max value of simulated screen.
    yRange : tuple of 2 floats
        Vertical (y) min/max value of simulated screen.
    pxWidth : int
        Number of horizontal pixels to use for the screen simulation.
        Vertical number is automatically computed to keep the correct
        simulated beam aspect ratio.
    pxHeight : int, optional
        Set this to an integer to prescribe pxHeight instead of pxWidth.
        The default is None.
    z : 1d array floats, optional
        Values from the interval [0.0, 1.0] for beam intensity modulation.
        Keep to None is unused.
        The default is None.
    oversample_t : int, optional
        Time oversampling factor. The time interval between two
        (x,y) points is divided by the line length in pixels times the
        oversampling factor. Higher values can give smoother results in some
        cases, but increase the computation time.
        The default is 3.
    psfSz : int, optional
        Size of the beam point spread function. Must be an odd value. Increase
        this value to get a fatter beam.
        The default is 9.
    psfDecay : float, optional
        Spatial decay of the beam point spread function. Higher values cause
        faster decay. get a fatter beam.
        The default is 3.
    cmap : matplotlib colormap, optional
        Colormap to use for plotting.
        The default is cmap_color_white(0.45, 0.6, bp=0.8).

    Returns
    -------
    im : imshow object
        Drawn scope screen.
    screen : 2d numpy array
        The beam exposore matrix.

    """
    
    if z is None:
        z = np.ones(len(x))
    
    # Must match the aspect ratio or the PSF gets squished.
    if pxHeight is None:
        pxHeight = int(pxWidth*np.diff(yRange)/np.diff(xRange))
    else:
        pxWidth = int(pxHeight*np.diff(yRange)/np.diff(xRange))
    
    psfOff = int((psfSz-1)/2)
    PSF = psf(psfSz, decay=psfDecay)
    
    # Convert input points to pixel coordinates
    px = (x-xRange[0])/(xRange[1]-xRange[0])*(pxWidth-1)
    py = (y-yRange[0])/(yRange[1]-yRange[0])*(pxHeight-1)
    
    # Calculate the length of each line segment.
    lens = np.sqrt((px[1:] - px[0:-1])**2 + (py[1:] - py[0:-1])**2)
    
    # Screen bitmap. Pad with PSF size
    screen = np.zeros((pxHeight+psfSz-1, pxWidth+psfSz-1))
    
    # Iterate over all line segments
    update_screen(np.ceil(lens*oversample_t), t, px, py, z, screen, 
                  pxHeight, pxWidth, PSF)
        
    # Remove PSF padding
    screen = screen[psfOff:-psfOff, psfOff:-psfOff]
    
    # Plot the result
    im = plt.gca().imshow(screen, cmap=cmap, origin='lower', aspect=1,
                    extent=(xRange[0], xRange[1], yRange[0], yRange[1]))
        
    return im, screen


