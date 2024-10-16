#!/usr/bin/env python

"""Module to create graphs from HWiNFO logging data."""

__author__ = "Jonathan Weber"
__version__ = "0.2"

import argparse
from datetime import datetime
import os
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd
from colors import ColorFactory
from colfams import ColFamInfo

ENCODING = "iso-8859-1"
DEFAULT_LAYOUT_NAME = "Custom"

def get_layout_name(argument: str) -> str:
    if not argument is None:
        p = Path(argument)
        if p.exists():
            return p.stem
        else:
            print(f"WARNING: Could not find layout at {p.absolute()}.")

    return DEFAULT_LAYOUT_NAME

def get_output_filename(timestamp: str, title: str, layout: str) -> str:
    filename = f'{timestamp}_{title}_{layout}'
    ext = ".png"

    fp = os.path.join(f"{filename}{ext}")
    counter = 0
    while Path(fp).exists():
        counter += 1
        fp = os.path.join(dir, f"{filename}{counter}{ext}")
        if counter > 1000:
            return None

    return fp

"""Extracts the unit of the measurement from the column name"""
def get_unit(colname: str) -> str:
    start = colname.rfind('[') + 1
    end = colname.rfind(']')
    return colname[start:end]

# interactively let the user choose which columns to select for drawing from a pandas frame
def select_columns(df) -> list[str]:
    # TODO colored output and display current selection
    selectedcols = []

    while (True):
        # list and choose from devices
        print()
        print("Please select a device.")
        devices = ColFamInfo.get_families()
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
        col_count = len(ColFamInfo.get_colnames(selected_device_name))
        for i in range (0, col_count):
            print(f"[{i}] {ColFamInfo.get_colnames(selected_device_name)[i]}")
        
        indices = input(f"Please select indices separated by spaces (or press ENTER to skip): ")
        if indices == '':
            continue

        index_list = indices.split(' ')
        for index in index_list:
            selectedcols.append(ColFamInfo.get_colnames(selected_device_name)[int(index)])
    
    return selectedcols

def main():
    parser = argparse.ArgumentParser(description="Parse a HwInfo log file (csv) and display selected data points in a set of graphs.")
    parser.add_argument("logfile", help="HwInfo log file containing the data to draw from.")
    parser.add_argument("-s", "--save", help="Write the figure to an image file instead of displaying it.", action='store_true')
    parser.add_argument("-e", "--export", help="Choose which values to draw and export the selection to a specified file. You can specify this selection later using the --layout option.", type=str)
    parser.add_argument("-l", "--layout", help="Specify a file that contains column names to draw the values from.", type=str)
    parser.add_argument("-f", "--format", help="Date format of datetimes in HwInfo log file. Note that the columns 'Date' and 'Time' should be combined using a whitespace. Defaults to: '%%d.%%m.%%Y %%H:%%M:%%S'", default="%d.%m.%Y %H:%M:%S")
    args = parser.parse_args()

    # get meta information
    LAYOUT_NAME = get_layout_name(args.layout)
    DATETIME_FORMAT = args.format
    if not " " in DATETIME_FORMAT:
        print("WARNING: Expected a single whitespace in the format string (-f) to separate date and time.")

    df = pd.read_csv(args.logfile, header=0, encoding=ENCODING)

    # retrieve recording date
    recording_date = f"{df['Date'][0]} {df['Time'][0]}"
    if "." in recording_date:
        recording_date = recording_date[:recording_date.rindex(".")] # strip miliseconds
    recording_date = datetime.strptime(recording_date, DATETIME_FORMAT)

    # match column families to columns
    ColFamInfo.init(df)
    
    # drop last two rows; they contain col family and header
    df = df.iloc[:-2]

    # compute timestamps relative to start of recording
    df['Time'] = df['Time'].replace(r"[.]\d*$", "", regex=True) # strip miliseconds
    df['Timestamps'] = df['Date'] + ' ' + df['Time']
    df['Timestamps'] = pd.to_datetime(df['Timestamps'], format=DATETIME_FORMAT)
    start_time = df['Timestamps'][0]
    df['Timestamps'] = df['Timestamps'].apply(lambda t: (t - start_time).seconds)
    df.drop(['Time', 'Date'], axis=1, inplace=True)

    # parse boolean values
    for name in df.columns:
        unit = get_unit(name)
        if unit == "Yes/No" or unit == "Ja/Nein":
            df[name] = df[name].apply(lambda value: int(value == "Yes" or value == "Ja"))
    
    # select cols from file
    selected_cols = []
    if not LAYOUT_NAME == DEFAULT_LAYOUT_NAME:
        try:
            with open(args.layout, "r", encoding=ENCODING) as file:
                selected_cols = file.readlines()
                for i in range(0, len(selected_cols)):
                    selected_cols[i] = selected_cols[i].replace("\n", "")
        except IOError as e:
            print(f"ERROR: Could not open layout {LAYOUT_NAME}.")
        
    # select cols interactively
    if len(selected_cols) == 0:
        selected_cols = select_columns(df)

    # export selection if specified using cmd line arg
    if not args.export == None and LAYOUT_NAME == DEFAULT_LAYOUT_NAME:
        head, tail = os.path.split(args.export)
        if (not head == "") and (not os.path.exists(head)):
            os.makedirs(head)

        # TODO prompt for override if tail exists

        try:
            with open(args.export, "w", encoding=ENCODING) as file:
                for colname in selected_cols:
                    file.write(colname + "\n")
            print(f"Layout saved as {args.export}")
            LAYOUT_NAME = get_layout_name(args.export)
        except IOError as e:
            print(e)  # TODO

    # sort into units
    cols_by_units = {}
    for name in selected_cols:
        unit = get_unit(name)
        if not unit in cols_by_units:
            cols_by_units[unit] = []
        
        cols_by_units[unit].append(name)

    # draw
    plotcount = len(cols_by_units.keys())
    values_x = df['Timestamps']
    fig, axes = plt.subplots(plotcount)

    if plotcount == 1:
        # turn axes into list if it wasnt already
        axes = [axes]

    title = f"{os.path.basename(args.logfile)}   |   {recording_date.strftime("%Y-%M-%d %H:%M:%S")}   |   Layout: {LAYOUT_NAME}"
    fig.suptitle(title)
    axes[plotcount - 1].set_xlabel("Time [s]")
    i = 0
    for unit in cols_by_units:
        for colname in cols_by_units[unit]:
            devicename = ColFamInfo.get_family(colname)
            if (devicename is None):
                print(f"WARNING: Could not find column '{colname}' in data.")
                continue

            values_y = df[colname]
            values_y = [float(x) for x in values_y]
            axes[i].plot(values_x, values_y, c=ColorFactory.next(), label=f"{colname} ({devicename})")

        axes[i].legend(loc="best", prop={"size": 11})
        axes[i].grid("both")
        axes[i].set_xticks(values_x)
        axes[i].tick_params(axis="x", labelsize=7, labelrotation=0)
        axes[i].set_ylabel(f"[{unit}]")
        ColorFactory.reset()
        i += 1

    # display or save figure
    if args.save:
        fp = get_output_filename(recording_date.strftime("%Y-%m-%d-%H%M%S"), Path(args.logfile).stem, LAYOUT_NAME)
        if fp is None:
            print("WARNING: Exceeded file limit for this configuration. Showing plot instead.")
            plt.show()
        else:
            fig.set_size_inches(24, 13.5)
            plt.savefig(fp, dpi=72, format='png')
            print(f"Figure written to {fp}")
    else:
        plt.show()

if __name__ == '__main__':
    main()