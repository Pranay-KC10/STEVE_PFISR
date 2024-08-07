# Import necessary libraries
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import os

# Custom path to the data file
path = "PFISR/"

# List all files in the directory
files = os.listdir(path)
files = [file for file in files if file.endswith('.h5')]  # Filter only .h5 files

for filename in files:
    # Open the data file of interest
    f = h5.File(path + filename, 'r')

    # Beam parameters
    beamcodes = f['BeamCodes']
    beamcodesdata = beamcodes[:, :].astype(float)

    # Epoch time
    epoch = f['UnixTime']
    epochData = epoch[:, :].astype(float)

    # Altitude
    alt = f['Altitude']
    altdata = alt[:, :] / 1000.  # Convert from meters to kilometers
    altdata = altdata.astype(float)

    # Plasma density
    ne = f['Ne']
    nedata = ne[:, :, :].astype(float)

    # Ion species
    ion = 0

    # Ion temperature
    ti = f['Fits']
    tidata = ti[:, :, :, ion, 1].astype(float)

    # Electron temperature
    te = f['Fits']
    tedata = te[:, :, :, -1, 1].astype(float)

    # Line-of-sight ion velocity
    losv = f['Fits']
    losvdata = losv[:, :, :, ion, 3].astype(float)

    # Close the data file
    f.close()

    # Convert epoch time to datetime
    ut = [datetime.datetime(int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[0]),  # YEAR
                            int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[1]),  # MONTH
                            int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[2]),  # DAY
                            int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[3]),  # HOUR
                            int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[4]),  # MINUTE
                            int(time.gmtime((epochData[t, 0] + epochData[t, 1]) / 2)[5]))  # SECOND
          for t in range(len(epochData))]

    altitudes = [275, 305]  # List of altitudes to process

    # Time range
    time_range = datetime.timedelta(hours=3)

    for altitude in altitudes:
        print(f"The current processing altitude is: {altitude} km")

        start_time = ut[0]  # Initialize start_time for each altitude
        end_time = start_time + time_range

        while start_time < ut[-1]:
            time_filter = [(ut[i] >= start_time) and (ut[i] <= end_time) for i in range(len(ut))]

            for i in range(len(altdata)):
                if beamcodesdata[i, 0] == 64157.0:  # Focus on beam parallel to magnetic field
                    a = abs(altdata[i, :] - altitude)
                    b = np.where(a == np.nanmin(a))
                    Ti = tidata[:, i, b[0]].flatten()
                    Te = tedata[:, i, b[0]].flatten()
                    Ne = nedata[:, i, b[0]].flatten()

                    filtered_ut = [ut[j] for j in range(len(ut)) if time_filter[j]]
                    filtered_Ti = [Ti[j] for j in range(len(Ti)) if time_filter[j]]
                    filtered_Ne = [Ne[j] for j in range(len(Ne)) if time_filter[j]]

                    Ti_avg = np.mean(filtered_Ti)
                    Ne_avg = np.mean(filtered_Ne)

                    # Initial thresholds
                    Ti_threshold = 140
                    Ne_threshold = 65

                    # Minimum thresholds
                    min_Ti_threshold = 100
                    min_Ne_threshold = 25

                    significant_changes = []

                    while Ti_threshold >= min_Ti_threshold and Ne_threshold >= min_Ne_threshold:
                        std_Ti = np.std(filtered_Ti)
                        std_Ne = np.std(filtered_Ne)

                        ratio_Ti = ((Ti_avg + std_Ti) / Ti_avg) * 100
                        ratio_Ne = ((Ne_avg - std_Ne) / Ne_avg) * 100

                        # Detect significant changes based on derivative thresholds
                        for t_index in range(len(filtered_ut)):
                            if ratio_Ti >= Ti_threshold and ratio_Ne <= Ne_threshold:
                                significant_changes.append(filtered_ut[t_index])

                        if significant_changes:
                            break  # Exit loop if significant changes are found
                        else:
                            Ti_threshold -= 20
                            Ne_threshold -= 20

                    if not significant_changes:
                        print(f"There are no events between: {start_time} and {end_time} at {altitude} km.")
                    else:
                        # Plotting Ti if there are significant changes
                        fig, ax1 = plt.subplots(figsize=(14, 7))

                        ax2 = ax1.twinx()
                        ax1.plot(filtered_ut, filtered_Ti, 'g-', label='Ti')
                        ax2.plot(filtered_ut, filtered_Ne, 'b-', label='Ne')

                        ax1.set_xlabel('Epoch Time')
                        ax1.set_ylabel('Line-of-Sight Ion Temperature [K]', color='g')
                        ax2.set_ylabel('Plasma Density [m-3]', color='b')

                        ax1.legend(loc='upper left')
                        ax2.legend(loc='upper right')

                        plt.title(f'Ti and Ne at {altitude} km')
                        plt.grid(True)

                        plotfile = 'PFISR/Ti_Ne-{}_{}_to_{}.png'.format(
                            altitude, start_time.strftime("%Y%m%d%H%M"), end_time.strftime("%Y%m%d%H%M"))
                        plt.savefig(plotfile)
                        plt.show()
                        plt.close()

            # Move to next time frame
            start_time = end_time
            end_time = start_time + time_range
