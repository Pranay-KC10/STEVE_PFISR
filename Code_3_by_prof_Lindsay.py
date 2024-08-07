import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import os

# CUSTOMIZE THE ALTITUDE SCALE (I RECOMMEND KEEPING BETWEEN 200 KM AND 400 KM)
alt_lowerlim = 200
alt_upperlim = 400

# CUSTOMIZE THE ION TEMPERATURE SCALE [K] 
# (POINTS WITH AN ERROR GREATER THAN THE MEASUREMENT ARE REMOVED)
ti_upperlim = 2300
ti_lowerlim = 200

# CUSTOMIZE THE PLASMA/ELECTRON DENSITY SCALE [m-3 IN LOG SCALE!] 
# (DATA WITH AN ERROR GREATER THAN THE MEASUREMENT ARE REMOVED)
nel_upperlim = 11.5
nel_lowerlim = 10.0

# CUSTOMIZE THE LINE-OF-SIGHT ION VELOCITY SCALE [m/s] 
# (DATA WITH AN ERROR GREATER THAN THE MEASUREMENT ARE KEPT SO DIFFUSION PROCESSES ARE VISIBLE)
losv_upperlim = 500
losv_lowerlim = -500

# CUSTOMIZE THE ELECTRON TEMPERATURE SCALE [K] 
# (DATA WITH AN ERROR GREATER THAN THE MEASUREMENT ARE REMOVED)
te_upperlim = 3000
te_lowerlim = 500

# CUSTOMIZE THE PATH TO THE DATAFILE RELATIVE TO THE CODE
path = "PFISR/"

# List all files in the directory
files = os.listdir(path)
files = [file for file in files if file.endswith('.h5')]  # Filter only .h5 files

for filename in files:

  # THIS OPTION ALLOWS YOU TO SELECT THE COLOR SCALE YOU WOULD LIKE TO USE. 'jet' IS
  # A COMMON OPTION, BUT IF YOU ARE COLOR BLIND YOU MAY CONSIDER 'viridis'
  colorscale = 'viridis'

  ################################################################################
  ################################################################################
  # UNLESS YOU ARE CUSTOMIZING THIS CODE, THERE IS NO NEED TO EDIT BELOW THIS LINE
  ################################################################################
  ################################################################################

  # THIS OPENS THE DATA FILE OF INTEREST
  f  = h5.File(path+filename, 'r')

  # BEAM PARAMETERS (E.G. ELEVATION ANGLE, AZIMUTH, ETC)
  beamcodes = f['BeamCodes']
  beamcodesdata = beamcodes[:,:]
  beamcodesdata = beamcodesdata.astype(float)    

  # EPOCH TIME
  epoch = f['UnixTime']
  epochData = epoch[:,:]
  epochData = epochData.astype(float)    

  # ALTITUDE
  alt = f['Altitude']
  altdata = alt[:,:]/1000. # CONVERTING FROM METERS TO KILOMETERS
  altdata = altdata.astype(float)    

  # PLASMA DENSITY [m-3]
  ne = f['Ne']
  nedata = ne[:,:,:]
  nedata = nedata.astype(float)    

  # ERROR IN PLASMA DENSITY [m-3]
  dne = f['dNe']
  dnedata = dne[:,:,:]
  dnedata = dnedata.astype(float)    

  # THE ION SPECIES IS SET
  # 0 = O+, THE DOMINANT F-REGION ION. SOME DATAFILES OFFER, 1 = O2+, 2 = NO+ , 
  # 3 = N2+ AND , 4 = N+, BUT I STRONGLY SUGGEST YOU DO NOT TOUCH THIS
  ion = 0

  # ION TEMPERATURE [K]
  ti = f['Fits']
  tidata = ti[:,:,:,ion,1]
  tidata = tidata.astype(float)    

  # ERROR IN ION TEMPERATURE [K]
  dti = f['Errors']
  dtidata = dti[:,:,:,ion,1]
  dtidata = dtidata.astype(float)    

  # ELECTRON TEMPERATURE [K]
  te = f['Fits']
  tedata = te[:,:,:,-1,1]  
  tedata = tedata.astype(float)    

  # ERROR IN ELECTRON TEMPERATURE [K]
  dte = f['Errors']
  dtedata = dte[:,:,:,-1,1]
  dtedata = dtedata.astype(float)    

  # LINE-OF-SIGHT ION VELOCITY [m/s]
  losv = f['Fits']
  losvdata = losv[:,:,:,ion,3]
  losvdata = losvdata.astype(float)    

  # CORRECTED GEOMAGNETIC LATITUDE [deg]
  lat = f['MagneticLatitude']
  latdata = lat[:,:]
  latdata = latdata.astype(float)       

  # CORRECTED GEOMAGNETIC LONGITUDE [deg]
  long = f['MagneticLongitude']
  longdata = long[:,:]
  longdata = longdata.astype(float)  

  # THIS CLOSES THE DATA FILE
  f.close() 

  # THIS CONVERTS EPOCH TIME TO UNIVERSAL TIME IN DATETIME
  ut = [datetime.datetime(int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[0]), # YEAR
                        int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[1]), # MONTH
                        int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[2]), # DAY
                        int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[3]), # HOUR
                        int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[4]), # MINUTE
                        int(time.gmtime((epochData[t,0]+epochData[t,1])/2)[5])) # SECOND
                        for t in range(len(epochData))]

  # SET TIME LIMITS BASED ON DATA
  time_lowerlim = ut[0]
  time_upperlim = ut[-1]

  # THE 2D GEOMETRY OF THE BEAMS IN CORRECTED GEOMAGNETIC COORDINATES IS DRAWN 
  for ii in range(len(longdata)):
    beamlat = []
    beamlong = []
    for jj in range(len(longdata[0])):  
      if ii+1 == 4:
          print(altdata[ii,jj],latdata[ii,jj],longdata[ii,jj])
      if alt_lowerlim < altdata[ii,jj] and altdata[ii,jj] < alt_upperlim:
        beamlat.extend([latdata[ii,jj]])
        if longdata[ii,jj] > 180:
          beamlong.extend([longdata[ii,jj]-360])
        if longdata[ii,jj] < 180:
          beamlong.extend([longdata[ii,jj]])
        #print(altdata[ii,jj],beamlat[-1],beamlong[-1])
    plt.plot(beamlong,beamlat,'k')
    plt.plot(beamlong,beamlat,'o')
    plt.text(beamlong[-1], beamlat[-1], 'Beam {}'.format(ii+1))

  # THE X-AXIS IS ALTERED SO VALUES NEAR 0 AND 360 APPEAR SIDE-BY-SIDE
  ax = plt.gca()
  ticks, _ = plt.xticks()
  ax.set_xticks(ticks)
  ax.set_xticklabels([int(tick) for tick in ticks])

  # THE FIGURE IS WRITTEN TO A FILE
  plt.title('Beam Locations in Corrected Geomagnetic Coordinates')  
  plt.xlabel('Corrected Geomagnetic Longitude [deg]')  
  plt.ylabel('Corrected Geomagnetic Latitude [deg]')  
  plt.grid(True)
  plotfile = 'PFISR/beam-map-{}.png'.format(filename)
  plt.savefig(plotfile)
  plt.cla()   # Clear axis
  plt.clf()   # Clear figure
  plt.close() # Close a figure window

  # ERRONEOUS POINTS ARE REMOVED (COMMENT THIS OUT TO VIEW ALL MEASUREMENTS)
  for tt in range(len(nedata)):
    for ii in range(len(nedata[0])):
      for jj in range(len(nedata[0,0])):
        if nedata[tt,ii,jj] < dnedata[tt,ii,jj]:
          nedata[tt,ii,jj] = np.NaN
        if tidata[tt,ii,jj] < dtidata[tt,ii,jj]:
          tidata[tt,ii,jj] = np.NaN
        if tedata[tt,ii,jj] < dtedata[tt,ii,jj]:
          tedata[tt,ii,jj] = np.NaN

  # WE CYCLE THROUGH THE DIFFERENT BEAMS IN THE EXPERIMENT
  for ii in range(len(longdata)):

    print('Generating Figures for Beam {} ...'.format(ii+1))
      
    # THE 2D GEOMETRY OF THE SELECTED BEAM IN CORRECTED GEOMAGNETIC COORDINATES IS DRAWN 
    beamlat = []
    beamlong = []
    for jj in range(len(longdata[0])):  
      if alt_lowerlim < altdata[ii,jj] and altdata[ii,jj] < alt_upperlim:
        beamlat.extend([latdata[ii,jj]])
        if longdata[ii,jj] > 180:
          beamlong.extend([longdata[ii,jj]-360])
        if longdata[ii,jj] < 180:
          beamlong.extend([longdata[ii,jj]])
    plt.plot(beamlong,beamlat,'k')
    plt.plot(beamlong,beamlat,'o')
    plt.text(beamlong[-1], beamlat[-1], 'Beam {}'.format(ii+1))

    # THE X-AXIS IS ALTERED SO VALUES NEAR 0 AND 360 APPEAR SIDE-BY-SIDE
    ax = plt.gca()
    ticks, _ = plt.xticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels([int(tick) for tick in ticks])

    # THE FIGURE IS WRITTEN TO A FILE
    plt.title('Beam {} Locations in Corrected Geomagnetic Coordinates'.format(ii+1))  
    plt.xlabel('Corrected Geomagnetic Longitude [deg]')  
    plt.ylabel('Corrected Geomagnetic Latitude [deg]')  
    plt.grid(True)
    plotfile = 'PFISR/beam{}-map-{}.png'.format(ii+1,filename)
    plt.savefig(plotfile)
    plt.cla()   # Clear axis
    plt.clf()   # Clear figure
    plt.close() # Close a figure window

    # THE FIGURE AXES ARE DEFINED
    fig, axarr = plt.subplots(2, 1, figsize=(10, 10))
    fig.suptitle('Beam {}: {}, {}, {}'.format(ii+1, filename, colorscale, datetime.datetime.now()))

    # THE X-AXIS IS TIME
    x = ut

    # THE ION TEMPERATURE IS PLACED IN THE FIRST PANEL
    y = altdata[ii,:]
    z = tidata[:,ii,:]
    # Handle non-finite values
    z = np.nan_to_num(z, nan=np.nanmean(z), posinf=np.nanmean(z), neginf=np.nanmean(z))
    plot = axarr[0].pcolormesh(x, y, z.T, cmap=colorscale)
    fig.colorbar(plot, ax=axarr[0])
    axarr[0].set_xlim([time_lowerlim, time_upperlim])
    axarr[0].set_ylim([alt_lowerlim, alt_upperlim])
    plot.set_clim([ti_lowerlim, ti_upperlim])
    axarr[0].set_title('Ion Temperature [K]')  
    axarr[0].set_ylabel('Altitude [km]')

    # THE PLASMA DENSITY IS PLACED IN THE SECOND PANEL
    y = altdata[ii,:]
    z = np.log10(nedata[:,ii,:])
    # Handle non-finite values
    z = np.nan_to_num(z, nan=np.nanmean(z), posinf=np.nanmean(z), neginf=np.nanmean(z))
    plot = axarr[1].pcolormesh(x, y, z.T, cmap=colorscale)
    fig.colorbar(plot, ax=axarr[1])
    axarr[1].set_xlim([time_lowerlim, time_upperlim])
    axarr[1].set_ylim([alt_lowerlim, alt_upperlim])
    plot.set_clim([nel_lowerlim, nel_upperlim])
    axarr[1].set_title('Plasma Density [m-3]')

    

    # THE FIGURE IS WRITTEN TO A FILE
    plotfile = 'PFISR/beam{}-parameters-{}.png'.format(ii+1,filename)
    plt.savefig(plotfile)
    plt.cla()   # Clear axis
    plt.clf()   # Clear figure
    plt.close() # Close a figure window
