import pandas as pd
import numpy as np

def trucking_preprocessing(input_path:str, machine_models_path:str, output_path:str):
    ## Trucking Data
    trucking = pd.read_csv(input_path, low_memory=False)
    trucking.columns = [x.upper() for x in trucking.columns]

    ############ convert string to date
    trucking['DATE'] = pd.to_datetime(trucking['DATE'], format='mixed')
    trucking['MONTH'] = trucking['DATE'].dt.strftime('%Y-%m')

    ############# Date of Analysis ##############
    data_start_date = '2000-01-01'
    trucking = trucking.loc[trucking.DATE >= data_start_date].reset_index(drop=True)

    ## distance column in raw data is distance per load. actual distance should be distance per load x number of loads. distance is in meters and not in KM
    trucking['DISTANCE'] = trucking.DISTANCE * trucking.NUMBEROFLOADS / 1000  ## divide by 1000 to convert to KM from METRES

    ########### Correct MACHINE TYPE AND MACHINE MODEL Data
    machine_models = pd.read_csv(machine_models_path)
    trucking = pd.merge(trucking, machine_models[['MANUFACTURERMODEL','MACHINETYPE','MACHINEMODEL']],on=['MANUFACTURERMODEL','MACHINETYPE'], how='left')
    ## remove any spcial characters including spaces. this is because machine model will be used as column name
    trucking.MACHINEMODEL = trucking.MACHINEMODEL.str.replace('\W', '_', regex=True) 

    ## remove any rows without a machinemodel
    trucking = trucking[~trucking.MACHINEMODEL.isna()].reset_index(drop=True)

    ### define Machine Shiftly Data
    trucking_machine_shiftly = trucking.groupby(['SITENAME','DATE', 'MONTH','MACHINECODE','MACHINETYPE','MACHINEMODEL', 'SHIFT'],as_index=False).agg(
          TONNES = ('TONNESRECONCILED', sum)
        , DISTANCE = ('DISTANCE', sum) ## this is actually distance per load
        , LOADS = ('NUMBEROFLOADS', sum)
        , TKM = ('TKM', sum)
        , BCMS = ('BCMS', sum)
        , M3 = ('M3', sum)
    )
    trucking_machine_shiftly['TONNES_PER_LOAD'] = np.where(trucking_machine_shiftly.LOADS >= 1 ,round(trucking_machine_shiftly.TONNES / trucking_machine_shiftly.LOADS, 1), np.nan)
    trucking_machine_shiftly['DISTANCE_PER_LOAD'] = np.where(trucking_machine_shiftly.LOADS >= 1 ,round(trucking_machine_shiftly.DISTANCE / trucking_machine_shiftly.LOADS,1), np.nan)
    trucking_machine_shiftly['SHIFT_COUNT'] = 1 #this is used in daily, n-daily and monthly sum aggregations if needed. every row is a machine shift
    trucking_machine_shiftly.to_csv(output_path, index=False)