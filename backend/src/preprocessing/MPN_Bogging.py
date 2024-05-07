import pandas as pd
import numpy as np

def bogging_preprocessing(input_path: str, output_path: str):
    bogging = pd.read_csv(input_path, low_memory=False)
    bogging.columns = [x.upper() for x in bogging.columns]

    bogging = Data_Quality_and_Adjustments(bogging)
    bogging = Activity_Identification(bogging)
    bogging = define_bogging_destination(bogging)
    bogging = define_Machine_Shiftly_Data(bogging)
    bogging.to_csv(output_path, index=False)



def Data_Quality_and_Adjustments(bogging):
    ############################### convert string to date
    bogging['DATE'] = pd.to_datetime(bogging['DATE'])
    bogging['MONTH'] = bogging.DATE.dt.strftime('%Y-%m')

    ############# Date of Analysis ##############
    data_start_date = '2000-01-01'
    bogging = bogging.loc[bogging.DATE >= data_start_date].reset_index(drop=True)

    ########################## REHANDLE Attribute: Tag rows with 'UG Stockpile' for bogging source as 'rehandle'
    bogging['REHANDLE'] = 0 + (bogging.BOGGINGSOURCENAME == 'UG Stockpile')

    ########################### REMOTE attribute
    bogging['REMOTE'] = 0+((0 + (bogging.REMOTEBOGGING == 'Yes') + \
                            (bogging.CONTRACTITEMNAME.str.contains('remote', case=False) | bogging.MATERIALTYPENAME.str.contains('remote', case=False) | bogging.JOBNUMBERDESC.str.contains('remote', case=False)) + \
                                (bogging.BOGGINGSOURCENAME == 'Stope')) >= 2)

    ########################### remove any entries with zero bogging tonnes
    bogging = bogging.loc[bogging.TONNESRECONCILED > 0].reset_index(drop=True)
    return bogging


def Activity_Identification(bogging):
    ############################### Sparse MATERIAL TYPE NAME for Material Type
    conditions = [
        (bogging.MATERIALTYPENAME.str.contains('fill', case=False, na=False))
        , (bogging.MATERIALTYPENAME.str.contains('CRF', case=False, na=False))
        , (bogging.MATERIALTYPENAME.str.contains('Ore|Grade|Marginal', case=False, regex=True, na=False) |
        bogging.MATERIALTYPENAME.str.contains('MG', case=True, na=False) |  ## MG = medium grade Ore
        bogging.MATERIALTYPENAME == 'ROM' # ROM is where Ore is taken
        )
        , (bogging.MATERIALTYPENAME.str.contains('Waste|NAF', case=False, regex=True, na=False) |   ### NAF is acid forming. it's Waste.
        bogging.MATERIALTYPENAME == 'Min'   #same as Mineralised Waste
        )
        , (bogging.MATERIALTYPENAME.str.contains('paste', case=False, na=False))
        , (bogging.MATERIALTYPENAME.str.contains('Road|MUD|Slurry|FIB|bore|raise', case=False, regex=True, na=False))]
    choices = ['BACKFILL','CRF','ORE','WASTE','PASTE','OTHER']
    bogging['MATERIAL_TYPE'] = np.select(conditions, choices, default=bogging.MATERIALTYPENAME)

    ############################### Sparse MATERIAL TYPE NAME for bogging ACTIVITY ---> this column is used for voting to decide activity
    conditions = [
        (bogging.MATERIAL_TYPE.str.contains('ROCKFILL|CRF|PASTE|PAF|CAF', case=False, regex=True, na=False))
        , (bogging.MATERIALTYPENAME.str.contains('Prod|stope', case=False, regex=True, na=False))
        , (bogging.MATERIALTYPENAME.str.contains('Dev', case=False, na=False))
        , (bogging.MATERIAL_TYPE.str.contains('OTHER', case=False, na=False))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT', 'OTHER']
    bogging['MATERIAL_ACTIVITY'] = np.select(conditions, choices, default='UNKNOWN')

    ############################### Sparse CONTRACTITEMNAME for bogging  ACTIVITY ---> this column is used for voting to decide activity
    conditions = [
        (bogging.CONTRACTITEMNAME.str.contains('fill|CRF', case=False, regex = True, na=False))
        , (bogging.CONTRACTITEMNAME.str.contains('Prod', case=False, na=False) )
        , (bogging.CONTRACTITEMNAME.str.contains('Dev', case=False, na=False))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['CONTRACT_ACTIVITY'] = np.select(conditions, choices, default='UNKNOWN')

    bogging.loc[(bogging.CONTRACT_ACTIVITY=='UNKNOWN') & bogging.CONTRACTITEMNAME.str.contains('manual|Stope', case=False, regex=True, na=False),'CONTRACT_ACTIVITY']='PRODUCTION'

    ############################### Sparse JOBNUMBERNMAE for bogging  ACTIVITY ---> this column is used for voting to decide activity
    conditions = [
        (bogging.JOBNUMBERDESC.str.contains('backf', case=False, na=False))
        , (bogging.JOBNUMBERDESC.str.contains('Prod|Prdn', case=False, regex=True, na=False))
        , (bogging.JOBNUMBERDESC.str.contains('Dev', case=False, na=False))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['JOBDESC_ACTIVITY'] = np.select(conditions, choices, default='UNKNOWN')

    ############################# Use material and contract activities with backfill, totruck and remote to vote for bogging activity
    conditions = [
        ((bogging.MATERIAL_ACTIVITY == 'UNKNOWN') & (bogging.CONTRACT_ACTIVITY == 'BACKFILL'))
        , ((bogging.MATERIAL_ACTIVITY == 'UNKNOWN') & (bogging.CONTRACT_ACTIVITY == 'PRODUCTION'))
        , (bogging.MATERIAL_ACTIVITY == 'UNKNOWN') & (bogging.CONTRACT_ACTIVITY == 'DEVELOPMENT')]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default='UNKNOWN')

    ############################# IF no activiy assigned, then further use material and contract activities with backfill, totruck and remote to vote for bogging activity
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'BACKFILL') + (bogging.CONTRACT_ACTIVITY == 'BACKFILL') + (bogging.BACKFILL == 'YES')) >= 2))
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'PRODUCTION') + (bogging.CONTRACT_ACTIVITY == 'PRODUCTION') + (bogging.BOGGINGSOURCENAME == 'Stope') ) >= 2))  
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'DEVELOPMENT') + (bogging.CONTRACT_ACTIVITY == 'DEVELOPMENT') + (bogging.BOGGINGSOURCENAME == 'Heading') ) >= 2))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if still no activity assigned, add job activity to material activity and contract activity for voting
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'BACKFILL') + (bogging.CONTRACT_ACTIVITY == 'BACKFILL') + (bogging.JOBDESC_ACTIVITY == 'BACKFILL') ) >= 2))
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'PRODUCTION') + (bogging.CONTRACT_ACTIVITY == 'PRODUCTION') + (bogging.JOBDESC_ACTIVITY == 'PRODUCTION') ) >= 2))  
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((0 + (bogging.MATERIAL_ACTIVITY == 'DEVELOPMENT') + (bogging.CONTRACT_ACTIVITY == 'DEVELOPMENT') + (bogging.JOBDESC_ACTIVITY == 'DEVELOPMENT') ) >= 2))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if still no activity assigned, Use job description
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.JOBDESC_ACTIVITY == 'BACKFILL'))
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.JOBDESC_ACTIVITY == 'PRODUCTION'))  
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.JOBDESC_ACTIVITY == 'DEVELOPMENT'))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if still no activity assigned, use contract activity alone
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & ((bogging.MATERIAL_ACTIVITY == 'BACKFILL') | (bogging.CONTRACT_ACTIVITY == 'BACKFILL')))
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.MATERIAL_ACTIVITY == 'PRODUCTION') & (bogging.CONTRACT_ACTIVITY == 'UNKNOWN'))  
        , ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & bogging.MATERIAL_ACTIVITY.str.contains('DEVELOPMENT|OTHER', regex=True) & bogging.CONTRACT_ACTIVITY.str.contains('DEVELOPMENT|UNKNOWN', regex=True))]
    choices = ['BACKFILL', 'PRODUCTION', 'DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if any left over unknown bogging activity has bogging source as "Stope", then tag its bogging activity as PRODUcTION
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.BOGGINGSOURCENAME == 'Stope'))  ]
    choices = ['PRODUCTION']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if any left over unknown bogging activity and material is WASTE and source is either stockpile or has heading, then tag its bogging activity as development
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & bogging.BOGGINGSOURCENAME.str.contains('Stockpile|Heading', case=False, regex=True) & (bogging.OREWASTE == 'WASTE')) ]
    choices = ['DEVELOPMENT']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)

    ############################# if any left over unknown bogging activity and material is ORE then tag its bogging activity as PRODUCTION
    conditions = [
        ((bogging.BOGGING_ACTIVITY == 'UNKNOWN') & (bogging.OREWASTE == 'ORE')) ]
    choices = ['PRODUCTION']
    bogging['BOGGING_ACTIVITY'] = np.select(conditions, choices, default=bogging.BOGGING_ACTIVITY)
    return bogging


def define_bogging_destination(bogging):
    ## boggers destination can either be a stockpile or a truck for Dev or production activities. For backfill it could be stockpile to Stope. So we will leave those as NA
    bogging['BOGGING_DESTINATION'] = np.where(bogging.TOUGLOCATIONNAME.isna(), 'Truck', 'Stockpile')  #if To location is NA then it's gone to truck. otherwise it's gone to a stockpile
    #if activity is BACKFILL, leave the destination blank because heading to stope is possible for backfill
    bogging['BOGGING_DESTINATION'] = np.where((bogging.BOGGING_ACTIVITY == 'BACKFILL') & (bogging.BOGGINGSOURCENAME.str.contains('Heading', case=False)), np.nan, bogging.BOGGING_DESTINATION)
    return bogging


def define_Machine_Shiftly_Data(bogging):
    bogging_machine_shiftly = (
        bogging
        .assign(
                BF_TONNES = bogging.TONNESRECONCILED.where(bogging.BOGGING_ACTIVITY == "BACKFILL")
            , PROD_TONNES = bogging.TONNESRECONCILED.where(bogging.BOGGING_ACTIVITY == "PRODUCTION")
            , DEV_TONNES = bogging.TONNESRECONCILED.where(bogging.BOGGING_ACTIVITY == "DEVELOPMENT")
            , RHDL_TONNES = bogging.TONNESRECONCILED.where(bogging.REHANDLE == 1)
            , REMOTE_TONNES = bogging.TONNESRECONCILED.where(bogging.REMOTE == 1) 
            , STOPE_STOCKPILE_TONNES = bogging.TONNESRECONCILED.where(bogging.BOGGINGSOURCENAME.str.contains('Stope', case=False) & (bogging.BOGGING_DESTINATION == 'Stockpile') & ~(bogging.BOGGING_ACTIVITY == 'BACKFILL'))
            , STOCKPILE_TRUCK_TONNES = bogging.TONNESRECONCILED.where((bogging.BOGGINGSOURCENAME == 'UG Stockpile') & (bogging.BOGGING_DESTINATION == 'Truck'))
            )
        .groupby(['SITENAME','DATE', 'MONTH','MACHINECODE','MACHINETYPE', 'SHIFT'],as_index=False).agg(
            TONNES = ('TONNESRECONCILED', sum)
            , BF_TONNES = ('BF_TONNES', sum)
            , PROD_TONNES = ('PROD_TONNES', sum)
            , DEV_TONNES = ('DEV_TONNES', sum)
            , RHDL_TONNES = ('RHDL_TONNES', sum)
            , REMOTE_TONNES = ('REMOTE_TONNES', sum)
            , STOPE_STOCKPILE_TONNES = ('STOPE_STOCKPILE_TONNES', sum)
            , STOCKPILE_TRUCK_TONNES = ('STOCKPILE_TRUCK_TONNES', sum)
        )
    )

    ##################################### set tonnes, BCMs, and buckets to NA if zero
    bogging_machine_shiftly.TONNES = np.where(bogging_machine_shiftly.TONNES == 0, np.nan, bogging_machine_shiftly.TONNES)
    bogging_machine_shiftly.BF_TONNES = np.where(bogging_machine_shiftly.BF_TONNES == 0, np.nan, bogging_machine_shiftly.BF_TONNES)
    bogging_machine_shiftly.PROD_TONNES = np.where(bogging_machine_shiftly.PROD_TONNES == 0, np.nan, bogging_machine_shiftly.PROD_TONNES)
    bogging_machine_shiftly.DEV_TONNES = np.where(bogging_machine_shiftly.DEV_TONNES == 0, np.nan, bogging_machine_shiftly.DEV_TONNES)
    bogging_machine_shiftly.RHDL_TONNES = np.where(bogging_machine_shiftly.RHDL_TONNES == 0, np.nan, bogging_machine_shiftly.RHDL_TONNES)
    bogging_machine_shiftly.REMOTE_TONNES = np.where(bogging_machine_shiftly.REMOTE_TONNES == 0, np.nan, bogging_machine_shiftly.REMOTE_TONNES)
    bogging_machine_shiftly.STOPE_STOCKPILE_TONNES = np.where(bogging_machine_shiftly.STOPE_STOCKPILE_TONNES == 0, np.nan, bogging_machine_shiftly.STOPE_STOCKPILE_TONNES)
    bogging_machine_shiftly.STOCKPILE_TRUCK_TONNES = np.where(bogging_machine_shiftly.STOCKPILE_TRUCK_TONNES == 0, np.nan, bogging_machine_shiftly.STOCKPILE_TRUCK_TONNES)

    bogging_machine_shiftly['SHIFT_COUNT'] = 1 #this is used in daily, n-daily and monthly sum aggregations if needed. every row is a machine shift
    return bogging_machine_shiftly
