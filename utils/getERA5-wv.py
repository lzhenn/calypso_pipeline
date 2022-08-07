import cdsapi
import datetime
for i in range(2010,2022):
    int_time_obj = datetime.datetime.strptime(str(i)+'0101', '%Y%m%d')
    end_time_obj = datetime.datetime.strptime(str(i)+'1231', '%Y%m%d')
    file_time_delta=datetime.timedelta(days=1)
    curr_time_obj = int_time_obj
    c = cdsapi.Client()

    # Area: North/West/South/East

    while curr_time_obj <= end_time_obj:
        
        #if curr_time_obj < datetime.datetime.strptime('20110924', '%Y%m%d'):
        #    curr_time_obj=curr_time_obj+file_time_delta
        #    continue

        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type':'reanalysis',
                'format':'grib',
                'variable':[
                   'mean_wave_direction', 'mean_wave_period', 
                   'significant_height_of_combined_wind_waves_and_swell',
                   'wave_spectral_directional_width',
                   ],
                'date':curr_time_obj.strftime('%Y%m%d'),
                'area':'60/80/-10/150',
                'time':[
                    '00:00',
                    '03:00',
                    '06:00',
                    '09:00',
                    '12:00',
                    '15:00',
                    '18:00',
                    '21:00',
                ]
            },
            curr_time_obj.strftime('%Y%m%d')+'-wv.grib')

        curr_time_obj=curr_time_obj+file_time_delta
