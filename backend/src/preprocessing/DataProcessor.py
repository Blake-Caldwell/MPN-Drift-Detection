#uploading just to let you guys know what i was thinking for the data processor
#still have to implement into whole system
#currently having isues with config object when running in full project but works when seperated
#currently the preprocess takes yaml object, input folder and output folder(can remove if you dont want to save it) 
#and returns arrays of activity dataframes and array of activity target columns
#can be easily scailed to add more sites with just another loop and array

import pandas as pd
from src.preprocessing.preprocessing import preprocessing

def preprocess(job):
    yaml = job['config']

    date_column = yaml['date_column']
    site_name = job['site_name']
    start_date = yaml['start_date']

    for activity in job['result']: 
        df = job['result'][activity]['data_frame']    

        df = preprocessing(df,activity ,site_name, start_date, add_tsfresh_features=False)
    
        df[date_column] = pd.to_datetime(df[date_column])

        job['result'][activity]['data_frame'] = df

    return job
