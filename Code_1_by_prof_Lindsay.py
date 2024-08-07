# THIS CODE WILL DOWNLOAD DATAFILES FROM "data.amisr.com" AND KEEP THE DATA NEEDED


# This imports the necessary libraries
import h5py as h5
import os 
import urllib
from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi
from urllib.error import HTTPError


# This reads in what data files will be downloaded
f1 = open('inputfile.TXT', 'r') 
files = f1.read().splitlines()
f1.close() 


# This will loop through the files listed in the input file
for t in range(len(files)):
  filename = str(files[t])
  filename1 = filename.split("_")[0]
  url = 'https://data.amisr.com/database/dbase_site_media/PFISR/Experiments/'+filename1+'/DataFiles/'+filename
  fileexists = -30
  
# This checks whether or not the requested file exists in the database
  try:
    urllib.request.urlretrieve(url, 'PFISR/'+filename)
  except urllib.error.HTTPError as err:
    print(err.code)
    fileexists = err.code

# If the error code does not change
  if fileexists == -30:  

# Download the file
    fs = h5.File('PFISR/'+filename, 'r')

# Create a file that will only contain the data we want
    fd = h5.File('PFISR/scrapped'+filename, 'w')

# Copy the data we want into the new file
    for a in fs.attrs:
      fd.attrs[a] = fs.attrs[a]

    for d in fs:
      if d != 'Calibration' and d != 'MSIS' and d != 'NeFromPower' and d != 'ProcessingParams' and d != 'Site' and d != 'FittedParams/Fits': 
        if d == 'FittedParams':
              fs.copy('FittedParams/Ne',fd)
              fs.copy('FittedParams/dNe',fd)
              fs.copy('FittedParams/Fits',fd)#:,:,:,0,3
              fs.copy('FittedParams/Errors/',fd)
              fs.copy('FittedParams/FitInfo',fd)

        if d == 'Geomag':
              fs.copy('Geomag/MagneticLatitude',fd)
              fs.copy('Geomag/MagneticLongitude',fd)
              fs.copy('Geomag/Latitude',fd)
              fs.copy('Geomag/Longitude',fd)
              fs.copy('Geomag/Altitude',fd)

        if d == 'Time':
              fs.copy('Time/Day',fd)
              fs.copy('Time/Month',fd)
              fs.copy('Time/Year',fd)
              fs.copy('Time/dtime',fd)
              fs.copy('Time/UnixTime',fd)
              fs.copy('Time/doy',fd)
 
        if d == 'BeamCodes':
          fs.copy('BeamCodes',fd)

    fs.close()
    fd.close()
    os.remove('PFISR/'+filename)



