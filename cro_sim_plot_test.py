#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    cro_sim_plot Test
    Copyright (C) 2023  Thomas Wiesner

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import matplotlib.pyplot as plt
import numpy as np
import os

import cro_sim_plot

import datetime

plotColorbars = False
saveFiles = True
imgdir = 'images/'

# %% Lissajous
xRange = (-1.1, 1.1)
yRange = (-1.1, 1.1)


t = np.linspace(0, 1, 1000)
x = np.sin(2*np.pi*t*2)
y = np.cos(2*np.pi*t*5)

# ---
figNr = 1
figSz = [8, 8]

plt.figure(num=figNr, figsize=figSz)


plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(x, y, t, xRange, yRange, pxWidth=2000, psfSz=17)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))

if plotColorbars:
    fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    ofile = os.path.join(imgdir, 'lissajous.png')
    plt.savefig(ofile, bbox_inches='tight')


# %% Noise
xRange = (-3, 3)
yRange = (-1, 1)

y = np.random.randn(500000)*0.2
x = np.linspace(xRange[0], xRange[1], len(y))
t = x

# ---
figNr = 2
figSz = [12, 12/3]

plt.figure(num=figNr, figsize=figSz)
plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(x, y, t, xRange, yRange, pxWidth=2000)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))

fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'noise.png'), bbox_inches='tight')

# Use colormap without fading to white for comparison
cm = cro_sim_plot.cmap_color_white(0.45, 1, bp=1.0001) # bp+eps > 1 to disable fading to white.
im[0].set_cmap(cm)

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'noise_nosat.png'), bbox_inches='tight')


# %% AM modulation
xRange = (0, 10)
yRange = (-2.5, 2.5)

t = np.linspace(0, 10, 100000)
x = t
y = np.sin(2*np.pi*t*80)*(1.1 + np.sin(2*np.pi*t/3))

# ---
figNr = 3
figSz = [12, 6]

plt.figure(num=figNr, figsize=figSz)
plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(x, y, t, xRange, yRange, pxWidth=2000)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))

if plotColorbars:
    fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'am_modulation.png'), bbox_inches='tight')

# Changing the color and grading
cm = cro_sim_plot.cmap_color_white(0.52, 0.8, bp=0.8)
im[0].set_cmap(cm)

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'am_modulation-cmap2.png'), bbox_inches='tight')

# Grid, if desired.
#plt.gca().grid(True)

# %% Beam intensity modulation
xRange = (0, 1)
yRange = (-0.2, 0.2)

t = np.linspace(0, 1, 100)
x = t
y = np.zeros(len(t))
z = x

# ---
figNr = 4
figSz = [8, 8]

plt.figure(num=figNr, figsize=figSz)
plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(x, y, t, xRange, yRange, pxWidth=2000, z=z, psfSz=21)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))


if plotColorbars:
    fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'beam_mod.png'), bbox_inches='tight')
    
# %% Beam intensity modulation. Creates a TV like raster line image
xRange = (-1, 1)
yRange = (-1, 1)

z = None

xv, yv = np.meshgrid(np.linspace(-1, 1, 100), np.linspace(-1, 1, 100))

xv = np.reshape(xv, (xv.size, 1)).flatten()
yv = np.reshape(yv, (yv.size, 1)).flatten()
t = np.linspace(0, 1, xv.size)

r = np.sqrt(xv**2 + yv**2)
z = np.sin(2*np.pi*r*3)/(2*np.pi*r*3)
z -= np.min(z)

# ---
figNr = 5
figSz = [8, 8]

plt.figure(num=figNr, figsize=figSz)
plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(xv, yv, t, xRange, yRange, pxWidth=2000, z=z, psfSz=21)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))


if plotColorbars:
    fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'beam_mod2.png'), bbox_inches='tight')

# %% Movement speed
xRange = (-1, 1)
yRange = (-0.25, 0.25)

t = np.array([0, 1, 1.5])
x = np.array([-1, 0, 1])
y = np.array([0, 0, 0])

# ---
figNr = 6
figSz = [8, 8]

plt.figure(num=figNr, figsize=figSz)
plt.clf()

fig, axs = plt.subplots(1, 1, num=figNr)

start = datetime.datetime.now()
im = cro_sim_plot.crt_plot(x, y, t, xRange, yRange, pxWidth=2000, psfSz=211, psfDecay=4)
stop = datetime.datetime.now()
print('Time elapsed: {}s'.format((stop-start).total_seconds()))

if plotColorbars:
    fig.colorbar(im[0])

fig.tight_layout()

if saveFiles:
    plt.savefig(os.path.join(imgdir, 'speed.png'), bbox_inches='tight')
