import argparse
from datetime import datetime
from matplotlib import pyplot as plt

import pandas as pd
import numpy as np
from colors import ColorFactory
from colfams import ColFamInfo

# TODO
# - encodings
# - parse booleans
# - date formats

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
    parser.add_argument("--export", help="Choose which values to draw and export the selection to a specified file. You can specify this selection later using the --layout option.", type=str)
    parser.add_argument("--layout", help="Specify a file that contains column names to draw the values from.", type=str)
    args = parser.parse_args()

    df = pd.read_csv(args.logfile, header=0, encoding="iso8859_15") # parse ja/nein as 1,0

    # match column families to columns
    ColFamInfo.init(df)
    
    # drop last two rows; they contain col family and header
    df = df.iloc[:-2]

    # compute timestamps relative to start of recording
    df['Time'] = df['Time'].replace("[.]\d*$", "", regex=True) # strip miliseconds
    df['Timestamps'] = df['Date'] + ' ' + df['Time']
    df['Timestamps'] = pd.to_datetime(df['Timestamps'], dayfirst=True)
    start_time = df['Timestamps'][0]
    df['Timestamps'] = df['Timestamps'].apply(lambda t: (t - start_time).seconds)
    df.drop(['Time', 'Date'], axis=1, inplace=True)
    
    # select cols from file
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

    # export selection if specified using cmd line arg
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
    values_x = df['Timestamps']
    fig, axes = plt.subplots(len(cols_by_units.keys()))
    fig.suptitle("Logging data")
    axes[len(cols_by_units.keys()) - 1].set_xlabel("Time [s]")
    i = 0
    for unit in cols_by_units:
        for colname in cols_by_units[unit]:
            devicename = ColFamInfo.get_family(colname)
            values_y = df[colname]
            values_y = [float(x) for x in values_y] # list comprehension
            axes[i].plot(values_x, values_y, c=ColorFactory.next(), label=f"{colname} ({devicename})")

        axes[i].legend(loc="best", prop={"size": 6})
        axes[i].grid("both")
        axes[i].set_xticks(values_x)
        axes[i].tick_params(axis="x", labelsize=7, labelrotation=0)
        axes[i].set_ylabel(f"Sensor data [{unit}]")
        ColorFactory.reset()
        i += 1

    plt.show()

if __name__ == '__main__':
    main()