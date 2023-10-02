def parsed_vence(df):
  df1=df[df.Latitude.str.contains("NA") == False]
  #store NA latitude values
  df_na_coordinates=df[df.Latitude.str.contains("NA") == True]
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
      out_df['Latitude']= pd.to_numeric(out_df['Latitude']) #convert lat to number
      out_df['Longitude']= pd.to_numeric(out_df['Longitude']) #convert long to number
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
          tz=tf.timezone_at(lng=out_df.Longitude.iloc[time_z], lat=out_df.Latitude.iloc[time_z])
          my_date_time=out_df.date.iloc[time_z]
          convert_time= my_date_time.astimezone(pytz.timezone(tz)).strftime('%Y-%m-%d %H:%M:%S %Z%z')
          #   print (tz)
          time_zone.append(tz)
          time_convert.append(convert_time)

      out_df['Time_Zone']=time_zone #create column for time zone
      out_df['date']=time_convert #convert to local
      out_df['date']=pd.to_datetime(out_df['date']) #convert to date
      #convert lat/long to utm
      Latitude=out_df['Latitude'] #changed
      Longitude=out_df['Longitude'] #changed
      Lat_utm=[]
      Long_utm=[]
      for f in range(0,len(Lat)):
          out=utm.from_latlon(Latitude.iloc[f],Longitude.iloc[f]) #changed
          #print (out)
          Lat_utm.append(out[0])
          Long_utm.append(out[1])
      out_df['Latitude_utm']=Lat_utm
      out_df['Longitude_utm']=Long_utm
      Lat_Long=pd.DataFrame({'Lat': out_df['Latitude_utm'],
         'Long': out_df['Longitude_utm'],})
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
      out_df['Distance']= np.sqrt ((out_df['Latitude_utm'].shift(1)-out_df['Latitude_utm'])**2 + (out_df['Longitude_utm'].shift(1) - out_df['Longitude_utm'])**2)

      out_df['Rate'] =out_df['Distance']/out_df['Duration']
      #remove points with rate of travel greater than 54m/min
      #print(len(out_df[out_df.Rate>54]))
      #out_df=out_df[out_df.Rate<54]

      #re_calculate after dropping fixes
      out_df['Distance']= np.sqrt ((out_df['Latitude_utm'].shift(1)-out_df['Latitude_utm'])**2 + (out_df['Longitude_utm'].shift(1) - out_df['Longitude_utm'])**2)
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
      geometry = [Point(xy) for xy in zip(out_df.Longitude,out_df.Latitude)]
      df_pts = out_df.drop(['Longitude', 'Latitude'], axis=1)
      df_pts['date']=df_pts['date'].astype(str)
      gdf = GeoDataFrame(df_pts, crs="EPSG:4326", geometry=geometry)

      return(gdf)

      #gdf.to_file(out_shp)

