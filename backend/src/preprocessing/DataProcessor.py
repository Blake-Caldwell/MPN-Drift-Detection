#uploading just to let you guys know what i was thinking for the data processor
#still have to implement into whole system
#currently having isues with config object when running in full project but works when seperated
#currently the preprocess takes yaml object, input folder and output folder(can remove if you dont want to save it) 
#and returns arrays of activity dataframes and array of activity target columns
#can be easily scailed to add more sites with just another loop and array

import yaml
from pathlib import Path
import pandas as pd
from backend.src.config.config import Config
from preprocessing import preprocessing

def preprocess(yaml, input_folder, preprocessed_data_folder):
    activity_dfs = []
    activity_target_column = []

    date_column = yaml['date_column']
    targets = yaml['targets']
    site_name = yaml['site_name']
    activity_list = yaml['activity_list']
    start_date = yaml['start_date']

    for activity in activity_list: 
        input_path = f"{input_folder}/mpn_{site_name}_{activity}.csv"
        #save_path = f"{preprocessed_data_folder}/preprocessed_{site_name}_{activity}.csv"
        df = preprocessing(input_path, None, activity, site_name, start_date, add_tsfresh_features=False)
    
        df[date_column] = pd.to_datetime(df[date_column])
        target_column = targets[activity]

        activity_dfs.append(df)
        activity_target_column.append(target_column)
    
    return(activity_dfs, activity_target_column)



#TESTING
config_p = Path(r'C:\Users\nicol_l3f7kpx\Documents\config.yaml')
csv_p = Path(r'C:\Users\nicol_l3f7kpx\Downloads\MPN_forecasring_backtest\MPN_forecasring_backtest\MPN_forecasring_backtest\bdm1_shiftly_processed')
save_p = Path(r'C:\Users\nicol_l3f7kpx\Documents\GitHub\MPN-Drift-Detection\backend\src\preprocessing\temp')

yaml_config = Config(config_p)

a_dfs, atc = preprocess(yaml_config, csv_p, save_p)
print(a_dfs)
print(atc)