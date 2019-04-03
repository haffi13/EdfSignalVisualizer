import pyedflib
import numpy as np
import os
import process_timer
import pandas as pd
import matplotlib.pyplot as plt, mpld3
from matplotlib.widgets import Slider
from matplotlib.collections import LineCollection
import math

pt = process_timer.Timer()

os.chdir(r'C:\ProjectResources')


class EdfData():
    def __init__(self, file_name):
        self.file = pyedflib.EdfReader(file_name)
        self.number_of_signals = self.file.signals_in_file
        self.duration = self.file.file_duration
        self.starttime = self.file.getStartdatetime()  # returns in format: 2019-01-20 03:28:03
        self.number_of_records = self.file.datarecords_in_file
        self.number_of_annotations = self.file.annotations_in_file
        self.labels = self.file.getSignalLabels()
        self.annotations = self.file.readAnnotations()
        self.recording_additional = self.file.getRecordingAdditional()

        # Setting fixed array sizes in accordance with the file format.
        self.labels = np.chararray(self.number_of_signals, 16, True)
        self.phys_dimensions = np.chararray(self.number_of_signals, 8, True)
        self.phys_max = self.phys_min = self.dig_max = self.dig_min = np.empty(self.number_of_signals)
        self.transducers = self.prefilters = np.chararray(self.number_of_signals, 80, True)
        self.sample_frequencies = self.file.getSampleFrequencies()

        self.signals = []

    # Set this function up so you can pass a list in with the signals you want, None = all signals.

    def get_data(self):
        pt.start()
        for channel in np.arange(self.number_of_signals):
            self.labels[channel] = self.file.getLabel(channel)
            self.phys_min[channel] = self.file.getPhysicalMinimum(channel)
            self.phys_max[channel] = self.file.getPhysicalMaximum(channel)
            self.phys_dimensions[channel] = self.file.getPhysicalDimension(channel)
            self.dig_min[channel] = self.file.getDigitalMinimum(channel)
            self.dig_max[channel] = self.file.getDigitalMaximum(channel)
            self.prefilters[channel] = self.file.getPrefilter(channel)
            self.transducers[channel] = self.file.getTransducer(channel)
            self.signals.append(self.file.readSignal(channel))


# The code below should later be put in another file. Here for convenience ATM...

D = EdfData('t.edf')
D.get_data()

# This is set up for the first signal, if there are different sampling rates this will break.
t = (np.arange(0.0, (len(D.signals[0]) / D.sample_frequencies[0]),
               (len(D.signals[0]) / D.sample_frequencies[0]) / len(D.signals[0])))
xticks = np.arange(0.0, len(D.signals[0]) / D.sample_frequencies[0], 1)
print('type(xticks) -> ' + str(type(xticks)))
xticks = xticks.tolist()  # is this needed ?
print('type(xticks) -> ' + str(type(xticks)))
dmin = math.floor(D.signals[0].min())
dmax = math.ceil(D.signals[0].max())
dr = (dmax - dmin) * 1.5
y0 = dmin
y1 = (len(D.signals) - 1) * dr + dmax

ticklocs = []  # Equal distribution on the Y axis, depending on number of signals.
segs = []  # Stores the signals in a manner that works with the LineCollection.
D.signals = np.array(D.signals)

for i in range(len(D.signals)):
    segs.append(np.column_stack((t, D.signals[i, :])))
    ticklocs.append(i * dr)

offsets = np.zeros((len(segs), 2), dtype=float)
offsets[:, 1] = ticklocs
fig = plt.figure()
ax = plt.subplot()
ax.set_xticks(xticks)
ax.set_yticks(ticklocs)
ax.set_xlim(0, 10)
ax.set_ylim(y0, y1)

lines = LineCollection(segs, offsets=offsets, transOffset=None)
ax.add_collection(lines)

plt.axis([0, 10, y0, y1])  # first 2 numbers are range that is visible at a time, last 2 are min/max for y axis
axpos = plt.axes([0.2, 0.01, 0.65, 0.03])  # position of the slider bar
spos = Slider(axpos, 'Pos', 0.5, 590)  # position, label, step size, length(max - visible range at a time)
ax.minorticks_off()


# Call update line from here. Use the params of udate line to get the x range it should be getting data from.
def update(val):
    pos = spos.val
    ax.axis([pos, pos + 10, y0, y1])
    fig.canvas.draw_idle()
    print('update')


plt.subplots_adjust(left=0.04, right=0.99, top=0.99, bottom=0.12, hspace=0.0)
spos.on_changed(update)
plt.show()

'''
print('t -> ' + str(t))
print('xticks -> ' + str(xticks))
print('dmin -> ' + str(dmin))
print('dmax -> ' + str(dmax))
print('dr -> ' + str(dr))
print('y0 -> ' + str(y0))
print('y1 -> ' + str(y1))
print('ticklocs -> ' + str(ticklocs))
print('len(ticklocs) -> ' + str(len(ticklocs)))
print('offsets -> ' + str(offsets))
#print('offsets.shape -> ' + str(offsets.shape))
#print('D.signals.shape -> ' + str(D.signals.shape))
print('len(D.signals) -> ' + str(len(D.signals)))
print('len(D.signals[0]) -> ' + str(len(D.signals[0])))
print('type(D.signals) -> ' + str(type(D.signals)))
print('type(D.signals[0]) -> ' + str(type(D.signals[0])))

# h1 is the name of the plot
def update_line(hl, new_data):
    hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()
'''
