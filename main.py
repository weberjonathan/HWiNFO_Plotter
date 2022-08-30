import argparse
from datetime import datetime
import time
from re import X
from shutil import which
from turtle import color
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import json
import random

import csv

import pandas as pd
import numpy as np
from colors import ColorFactory

def match_column_families(families, colnames):
    rtn = {}
    for i in range(0, len(families)):
        key = families[i]
        if not type(key) is str:
            continue

        if not key in rtn:
            rtn[key] = []

        rtn[key].append(colnames[i])

    return rtn

# interactively let the user choose which columns to select for drawing from a pandas frame
def select_columns(df) -> list[str]:
    # TODO colored output and display current selection
    system_dict = match_column_families(df.iloc[-1], df.columns.values)
    selectedcols = []

    while (True):
        # list and choose from devices
        print()
        print("Please select a device.")
        devices = list(system_dict.keys())
        for i in range(0, len(devices)):
            print(f"[{i}] {devices[i]}")
            i += 1
        device_index = input(f"Please select a device by entering its index. To confirm your selection press ENTER on an empty line. ")
        if (device_index == ""):
            break

        device_index = int(device_index) # TODO validate
        selected_device_name = devices[device_index]
        print()

        # list and choose from columns belonging to selected device
        print(f"Selected device: {selected_device_name}")
        rangeub = len(system_dict[selected_device_name])
        for i in range (0, rangeub):
            print(f"[{i}] {system_dict[selected_device_name][i]}")
        
        indices = input(f"Please select indices separated by spaces (or press ENTER to skip): ")
        if indices == '':
            continue

        index_list = indices.split(' ')
        for index in index_list:
            selectedcols.append(system_dict[selected_device_name][int(index)])
    
    return selectedcols

# timestamps expected as list of timestamps with miliseconds like so 14:56:0.332
def get_x_labels(timestamps, format: str = "%H:%M:%S"):
    labels_x = []
    start = datetime.strptime(timestamps[0][0:8], format)
    for j in range(0, len(timestamps)):
        
        delta = ""
        try:
            current = datetime.strptime(timestamps[j][0:timestamps[j].find(".")], format)
            delta = current - start
        except ValueError as e:
            print(e)
        
        labels_x.append(str(delta.seconds))

    return labels_x


def main():
    parser = argparse.ArgumentParser(description="Parse a HwInfo log file (csv) and display selected data points in a set of graphs.")
    parser.add_argument("logfile", help="HwInfo log file containing the data to draw from.")
    parser.add_argument("--export", help="Choose which values to draw and export the selection to a specified file. You can specify this selection later using the --layout option.", type=str)
    parser.add_argument("--layout", help="Specify a file that contains column names to draw the values from.", type=str)
    args = parser.parse_args()

    df = pd.read_csv(args.logfile, header=0, encoding="iso8859_15")

    # select cols
    selected_cols = []
    if not args.layout == None:
        try:
            with open(args.layout, "r", encoding="iso8859_15") as file:
                selected_cols = file.readlines()
                for i in range(0, len(selected_cols)):
                    selected_cols[i] = selected_cols[i].replace("\n", "")
        except IOError as e:
            print(e)  # TODO
        
    # select cols interactively
    if len(selected_cols) == 0:
        selected_cols = select_columns(df)

    # check if export mode
    if not args.export == None and args.layout == None:
        try:
            with open(args.export, "w", encoding="iso8859_15") as file:
                for colname in selected_cols:
                    file.write(colname + "\n")
        except IOError as e:
            print(e)  # TODO

    # sort into units
    cols_by_units = {}
    for name in selected_cols:
        start = name.rfind('[') + 1
        end = name.rfind(']')
        unit = name[start:end]

        if not unit in cols_by_units:
            cols_by_units[unit] = []
        
        cols_by_units[unit].append(name)

    # draw
    values_x = df['Time'].iloc[:-2]
    labels_x = get_x_labels(values_x)
    fig, axes = plt.subplots(len(cols_by_units.keys()))
    fig.suptitle("Logging data")
    axes[len(cols_by_units.keys()) - 1].set_xlabel("Time [s]")
    i = 0
    for unit in cols_by_units:
        for colname in cols_by_units[unit]:
            devicename = df[colname].iloc[-1]
            values_y = df[colname].iloc[:-2]
            values_y = [float(x) for x in values_y] # list comprehension
            axes[i].plot(values_x, values_y, c=ColorFactory.next(), label=f"{colname} ({devicename})")

        axes[i].legend(loc="best", prop={"size": 6})
        axes[i].grid("both")
        axes[i].set_xticks(range(0, len(values_x), 1), labels=labels_x)
        axes[i].tick_params(axis="x", labelsize=7, labelrotation=0)
        axes[i].set_ylabel(f"Sensor data [{unit}]")
        ColorFactory.reset()
        i += 1

    # fig: Figure = plt.figure()
    # values_x = df['Time'].iloc[:-2]

    # plot_index = 1
    # for unit in cols_by_units:
    #     subplot = fig.add_subplot(len(cols_by_units.keys()), 1, plot_index)
    #     plot_index += 1

    #     for colname in cols_by_units[unit]:
    #         values_y = df[colname].iloc[:-2]
    #         values_y = [float(x) for x in values_y] # list comprehension
    #         subplot.plot(values_x, values_y, c='red', label=colname)

    # TODO legende und y label für alle subplots
    # colnames sollten maps haben für zugehörige familie und farben

    # https://www.tutorialspoint.com/matplotlib-legends-in-subplot

    # draw
    # plt.plot(values_x, values_y1, c='red', label='red test')
    # plt.plot(values_x, values_y2, c='blue', label='blue test')
    # plt.xlabel("Price (EUR)")
    # plt.ylabel("Rasterization performance (Avg FPS, 1080p)")
    # plt.title(f'Price per Performance {date.today()}')

    # offset = 0
    # for i in range(0, len(gpu_data)):
    #     if isDrawableGpu(gpu_data[i]):
    #         x_text = gpu_data[i]['pricing']
    #         y_text = gpu_data[i]['performance']
    #         text = gpu_data[i]['name']
    #         plt.text(x_text, y_text, text, c = colors[i - offset])
    #     else:
    #         offset = offset + 1

    #     if 'msrp' in gpu_data[i]:
    #         x_text = gpu_data[i]['msrp']
    #         y_text = gpu_data[i]['performance']
    #         text = gpu_data[i]['name']
    #         plt.text(x_text, y_text, text, c = 'lightgray')

    # # x-axis layout
    # step_x = 100
    # ub_x = 2000
    # plt.xticks(range(0, ub_x + 1, step_x))

    # # y axis layout
    # step_y = 25
    # ub_y = 150
    # plt.yticks(range(0, ub_y + 1, step_y))

    # show
    # plt.legend(loc="upper left")
    # plt.grid(which="both")
    plt.show()

if __name__ == '__main__':
    main()