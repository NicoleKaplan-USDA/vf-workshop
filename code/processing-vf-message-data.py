import math
#from utm.error import OutOfRangeError

__all__ = ['to_latlon', 'from_latlon']

K0 = 0.9996

E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)

SQRT_E = math.sqrt(1 - E)
_E = (1 - SQRT_E) / (1 + SQRT_E)
_E2 = _E * _E
_E3 = _E2 * _E
_E4 = _E3 * _E
_E5 = _E4 * _E

M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
M3 = (15 * E2 / 256 + 45 * E3 / 1024)
M4 = (35 * E3 / 3072)

P2 = (3. / 2 * _E - 27. / 32 * _E3 + 269. / 512 * _E5)
P3 = (21. / 16 * _E2 - 55. / 32 * _E4)
P4 = (151. / 96 * _E3 - 417. / 128 * _E5)
P5 = (1097. / 512 * _E4)

R = 6378137

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None, strict=True):
    """This function convert an UTM coordinate into Latitude and Longitude

        Parameters
        ----------
        easting: int
            Easting value of UTM coordinate

        northing: int
            Northing value of UTM coordinate

        zone number: int
            Zone Number is represented with global map numbers of an UTM Zone
            Numbers Map. More information see utmzones [1]_

        zone_letter: str
            Zone Letter can be represented as string values. Where UTM Zone
            Designators can be accessed in [1]_

        northern: bool
            You can set True or False to set this parameter. Default is None


       .. _[1]: http://www.jaworski.ca/utmzones.htm

    """
    if not zone_letter and northern is None:
        raise ValueError('either zone_letter or northern needs to be set')

    elif zone_letter and northern is not None:
        raise ValueError('set either zone_letter or northern, but not both')

    if strict:
        if not 100000 <= easting < 1000000:
            raise OutOfRangeError('easting out of range (must be between 100.000 m and 999.999 m)')
        if not 0 <= northing <= 10000000:
            raise OutOfRangeError('northing out of range (must be between 0 m and 10.000.000 m)')
    if not 1 <= zone_number <= 60:
        raise OutOfRangeError('zone number out of range (must be between 1 and 60)')

    if zone_letter:
        zone_letter = zone_letter.upper()

        if not 'C' <= zone_letter <= 'X' or zone_letter in ['I', 'O']:
            raise OutOfRangeError('zone letter out of range (must be between C and X)')

        northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * math.sin(2 * mu) +
             P3 * math.sin(4 * mu) +
             P4 * math.sin(6 * mu) +
             P5 * math.sin(8 * mu))

    p_sin = math.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = math.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = math.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = _E * p_cos**2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                 d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return (math.degrees(latitude),
            math.degrees(longitude) + zone_number_to_central_longitude(zone_number))


def from_latlon(latitude, longitude, force_zone_number=None):
    """This function convert Latitude and Longitude to UTM coordinate

        Parameters
        ----------
        latitude: float
            Latitude between 80 deg S and 84 deg N, e.g. (-80.0 to 84.0)

        longitude: float
            Longitude between 180 deg W and 180 deg E, e.g. (-180.0 to 180.0).

        force_zone number: int
            Zone Number is represented with global map numbers of an UTM Zone
            Numbers Map. You may force conversion including one UTM Zone Number.
            More information see utmzones [1]_

       .. _[1]: http://www.jaworski.ca/utmzones.htm
    """
    if not -80.0 <= latitude <= 84.0:
        raise OutOfRangeError('latitude out of range (must be between 80 deg S and 84 deg N)')
    if not -180.0 <= longitude <= 180.0:
        raise OutOfRangeError('longitude out of range (must be between 180 deg W and 180 deg E)')

    lat_rad = math.radians(latitude)
    lat_sin = math.sin(lat_rad)
    lat_cos = math.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan * lat_tan
    lat_tan4 = lat_tan2 * lat_tan2

    if force_zone_number is None:
        zone_number = latlon_to_zone_number(latitude, longitude)
    else:
        zone_number = force_zone_number

    zone_letter = latitude_to_zone_letter(latitude)

    lon_rad = math.radians(longitude)
    central_lon = zone_number_to_central_longitude(zone_number)
    central_lon_rad = math.radians(central_lon)

    n = R / math.sqrt(1 - E * lat_sin**2)
    c = E_P2 * lat_cos**2

    a = lat_cos * (lon_rad - central_lon_rad)
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    m = R * (M1 * lat_rad -
             M2 * math.sin(2 * lat_rad) +
             M3 * math.sin(4 * lat_rad) -
             M4 * math.sin(6 * lat_rad))

    easting = K0 * n * (a +
                        a3 / 6 * (1 - lat_tan2 + c) +
                        a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)) + 500000

    northing = K0 * (m + n * lat_tan * (a2 / 2 +
                                        a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c**2) +
                                        a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)))

    if latitude < 0:
        northing += 10000000

    return easting, northing, zone_number, zone_letter


def latitude_to_zone_letter(latitude):
    if -80 <= latitude <= 84:
        return ZONE_LETTERS[int(latitude + 80) >> 3]
    else:
        return None


def latlon_to_zone_number(latitude, longitude):
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        return 32

    if 72 <= latitude <= 84 and longitude >= 0:
        if longitude <= 9:
            return 31
        elif longitude <= 21:
            return 33
        elif longitude <= 33:
            return 35
        elif longitude <= 42:
            return 37

    return int((longitude + 180) / 6) + 1


def zone_number_to_central_longitude(zone_number):
    return (zone_number - 1) * 6 - 180 + 3

def process_vf_data(df):
  import os
  import sys
  import re
  import warnings
  import requests
  from requests.structures import CaseInsensitiveDict
  import datetime
  import pandas as pd
  import json
  import numpy as np
  import pytz
  import utm
  #import utm
  from shapely.geometry import Point
  from geopandas import GeoDataFrame
  df1=df[df.latitude.str.contains("NA") == False]
  #store NA latitude values
  df_na_coordinates=df[df.latitude.str.contains("NA") == True]
#get unique collar id as last 4 characters in mac address
  df1['collar_id']= df1['collar'].str[-4:]
  #create list of unique collars
  collars=df1.collar_id.unique()
  #collars
  #change working directory to google drive location
  cwd= '/content/drive/My Drive/Vence_API'

#loop through each unique collar ID and process data
  for i in range(0, len(collars)):

      #subset out data based on collar id number in loop
      out_df = df1[df1["collar_id"] ==collars[i]]
      out_df['latitude']= pd.to_numeric(out_df['latitude']) #convert lat to number
      out_df['longitude']= pd.to_numeric(out_df['longitude']) #convert long to number
      out_df['date']=pd.to_datetime(out_df['date'],utc=True)  #convert date to date UTC
      out_df = out_df.sort_values([ "date"], ascending = ( True)) #sort by date
      out_df ['Duration']=out_df ['date']-out_df ['date'].shift(1) #calculate duration between successive fixes
      out_df['Duration']=out_df['Duration']/np.timedelta64(1, 's')/60  #convert to minutes
      from timezonefinder import TimezoneFinder
      tf = TimezoneFinder()

      time_zone=[]
      time_convert=[]
      #loop through each lat long and get the local timezone for each point and make list of converted date/time
      for time_z in range(0,len(out_df)):
          tz=tf.timezone_at(lng=out_df.longitude.iloc[time_z], lat=out_df.latitude.iloc[time_z])
          my_date_time=out_df.date.iloc[time_z]
          convert_time= my_date_time.astimezone(pytz.timezone(tz)).strftime('%Y-%m-%d %H:%M:%S %Z%z')
          #   print (tz)
          time_zone.append(tz)
          time_convert.append(convert_time)

      out_df['Time_Zone']=time_zone #create column for time zone
      out_df['date']=time_convert #convert to local
      out_df['date']=pd.to_datetime(out_df['date']) #convert to date
      #convert lat/long to utm
      Latitude=out_df['latitude'] #changed
      Longitude=out_df['longitude'] #changed
      Lat_utm=[]
      Long_utm=[]
      for f in range(0,len(Lat)):
          out=utm.from_latlon(Latitude.iloc[f],Longitude.iloc[f]) #changed
          #print (out)
          Lat_utm.append(out[0])
          Long_utm.append(out[1])
      out_df['latitude_utm']=Lat_utm
      out_df['longitude_utm']=Long_utm
      Lat_Long=pd.DataFrame({'Lat': out_df['latitude_utm'],
         'Long': out_df['longitude_utm'],})
      #create kd tree to get number of points within 30m +- 20 points form each
      counts=[]
      count_sum=[]
      from sklearn.neighbors import KDTree

      for m in range(0,len(out_df)):

          t=20 #this is for 20 points 20+ and 20-
          b=m-t
          if b <0:
              b=0
          e=m+t
          if e>len(Lat_Long):
              e=len(Lat_Long)
          #Lat_Long[b:e]
          gps_tree = KDTree(Lat_Long[b:e])
          ##count within 10m radius
          ct=gps_tree.query_radius(Lat_Long[b:e],r=30,count_only=True) #can change radius r to whatever this is set to 30m
          if m < t:
              counts.append(ct[m])
          else:
              counts.append(ct[t])
          count_sum.append(ct.sum())


      out_df['Count']=counts #create count column
      out_df['Sum']=count_sum #creat sum column

      #flag collars that have been stationary for a long period of time, indicates collar fell off
      out_df['Flag'] = np.where( (out_df['Sum'] >= 800), 1,0)
      from itertools import groupby
      count_dups = [sum(1 for _ in group) for _, group in groupby(out_df['Flag'])]
      new=[]
      for p in range (0,len(count_dups)):
          a=np.repeat(count_dups[p], count_dups[p], axis=0)
          new.append(a)
      count_vector=np.hstack(new)
      out_df['Count_Flag']=count_vector
      out_df['Count_Flag'] = np.where(out_df['Flag'] == 0, 0, out_df['Count_Flag'])
      #at 576 this would be equivalent to 5 minute fix data not moving for 2 days
      out_df['Flag_Collar_Off']=np.where(out_df['Count_Flag'] >= 576, 'Flag','Ok')
      out_df.drop(['Count', 'Flag','Count_Flag'], axis=1, inplace=True)







      #calculate euclidean distance
      out_df['Distance']= np.sqrt ((out_df['latitude_utm'].shift(1)-out_df['latitude_utm'])**2 + (out_df['longitude_utm'].shift(1) - out_df['longitude_utm'])**2)

      out_df['Rate'] =out_df['Distance']/out_df['Duration']
      #remove points with rate of travel greater than 54m/min
      #print(len(out_df[out_df.Rate>54]))
      #out_df=out_df[out_df.Rate<54]

      #re_calculate after dropping fixes
      out_df['Distance']= np.sqrt ((out_df['latitude_utm'].shift(1)-out_df['latitude_utm'])**2 + (out_df['longitude_utm'].shift(1) - out_df['longitude_utm'])**2)
      out_df ['Duration']=out_df ['date']-out_df ['date'].shift(1)
      out_df['Duration']=out_df['Duration']/np.timedelta64(1, 's')/60
      out_df['Rate'] =out_df['Distance']/out_df['Duration']

      #conditions=[
      #    (out_df['Rate'] <2.34),
      #    (out_df['Rate'] >=2.34)&(out_df['Rate'] <=25),
      #    (out_df['Rate'] >25)]
      #choices=["Rest","Graze","Walk"]
      #out_df['Behavior']=np.select(conditions,choices)



      out_csv='/content/drive/My Drive/Vence_API/csv_files/' + collars[i] +'.csv'

      out_shp='/content/drive/My Drive/Vence_API/shp_files/'  + collars[i]  +'.shp'


      out_df.to_csv(out_csv)
      geometry = [Point(xy) for xy in zip(out_df.longitude,out_df.latitude)]
      df_pts = out_df.drop(['longitude', 'latitude'], axis=1)
      df_pts['date']=df_pts['date'].astype(str)
      gdf = GeoDataFrame(df_pts, crs="EPSG:4326", geometry=geometry)



      gdf.to_file(out_shp)


