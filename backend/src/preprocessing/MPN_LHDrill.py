import pandas as pd
import numpy as np
import math
from sklearn.cluster import DBSCAN


def LH_preprocessing(input_path:str, output_path:str, machine_shiftly_hours_path:str):
    lh_drill = pd.read_csv(input_path, low_memory=False)
    lh_drill.columns = [x.upper() for x in lh_drill.columns]
    machine_shiftly_hours = pd.read_csv(machine_shiftly_hours_path, low_memory=False)

    lh_drill = Data_Quality_and_Adjustments(lh_drill)
    lh_drill = operator_shiftly_data(lh_drill)
    lh_drill_machine_shiftly = data_quality(lh_drill)
    lh_drill_hours_machine_shiftly_agg = run_hours_data(lh_drill_machine_shiftly, machine_shiftly_hours, lh_drill)
    lh_drill_machine_shiftly = penetration_rate_for_shiftly(lh_drill_hours_machine_shiftly_agg, lh_drill_machine_shiftly)
    lh_drill_machine_shiftly.to_csv(output_path, index=False)




def create_na_group(rollback_col):
    """
    This function takes a dataframe Series (column) and outputs a grouping column that groups rows with consecutive
    NA values with the first next row that is not NA. This grouping enables aggregating those rows
    """  
    try:

        a = ~rollback_col.isna() + 0  # 1 if rollback_col has value
        b = a.replace(0, np.nan)      # creates a series where is 1 if has value and null if roll_back_col has no value

        c = rollback_col.index        # get the index of rows that have value
        d = c*b                       # creates a series where it's value of index if it has value or NA if roll_back_col has no value
        d = d.bfill()                 # back fill the NAs in the series so that the above NA rows have the same index value as the one below them with value. This is the grouping
        d = round(d)                  # make the grouping an INT output
        return(d)

    except Exception as e:
        print(e.message)
        return None


def detect_outlier_dbscan(input_col, **kwargs):
    """
    This function takes a dataframe Series (column) and outputs a grouping of clusters with -1 as anomaly rows
    """    

    try:
        
        outlier_detection = DBSCAN(**kwargs)
        clusters = outlier_detection.fit_predict(input_col.to_numpy().reshape(-1, 1))
        return (clusters)

    except Exception as e:
        print(e.message)
        return None
    

def Data_Quality_and_Adjustments(lh_drill, remove_cleaning_meters=True, remove_misc_meters=True):
    lh_drill['DATE'] = pd.to_datetime(lh_drill['DATE'])
    lh_drill['MONTH'] = lh_drill['DATE'].dt.strftime('%Y-%m')
    data_start_date = '2000-01-01'
    lh_drill = lh_drill.loc[lh_drill.DATE >= data_start_date].reset_index(drop=True)

    ############################### Correct MACHINE TYPE AND MACHINE MODEL Data
    lh_drill.loc[lh_drill.MACHINETYPE == 'SANDVIK DL430-7 108A13649-1', 'MACHINETYPE'] = 'SANDVIK DL430-7'
    lh_drill.loc[lh_drill.MACHINETYPE == 'SOLO DL420-15C 107A12026-1', 'MACHINETYPE'] = 'SOLO DL420-15C'


    ### remove cleaning meters before calculating equivalent meters. make sure to include redrill meters as it's used as a parameter
    lh_drill['CLEANING_METERS'] = lh_drill.LONGHOLEMETRES.where(~lh_drill.ISREDRILL & lh_drill.CONTRACTITEMNAME.str.contains('clean', case = False))
    lh_drill['MISC_METERS'] = lh_drill.LONGHOLEMETRES.where(~lh_drill.ISREDRILL & lh_drill.CONTRACTITEMNAME.str.contains('Sludge|Misc|Service', case = False))

    if remove_cleaning_meters:
        lh_drill = lh_drill.loc[lh_drill.CLEANING_METERS.isna()].reset_index(drop=True)
    if remove_misc_meters:
        lh_drill = lh_drill.loc[lh_drill.MISC_METERS.isna()].reset_index(drop=True)

    ################################ calculate equivalent meteres and determine hole and activity type (hole ID by three attributes of location, ring number and hole number)
    lh_drill['HOLE_ID'] = lh_drill.UGLOCATIONNAME + '_' + lh_drill.RINGNUMBER + '_' + lh_drill.HOLENUMBER
    hole_size = lh_drill[['SITENAME','HOLE_ID','LONGHOLEDIAMETER']].drop_duplicates()
    hole_size = hole_size.sort_values(by=['SITENAME','HOLE_ID', 'LONGHOLEDIAMETER']).reset_index(drop = True)
    hole_size['LONGHOLE_CROSS_SEC_AREA'] = np.power((hole_size.LONGHOLEDIAMETER/1000/2),2)*math.pi
    hole_size['PILOT_HOLE_CROSS_SECTION_AREA'] = hole_size.groupby(['SITENAME','HOLE_ID']).LONGHOLE_CROSS_SEC_AREA.transform('min') # pilot hole is the smallest hole size
    hole_size['PREV_LONGHOLEDIAMETER'] = hole_size.groupby(['SITENAME','HOLE_ID']).LONGHOLEDIAMETER.shift() #get the previous hole size if exists for reaming
    hole_size.loc[hole_size.PREV_LONGHOLEDIAMETER.isna(), 'PREV_LONGHOLEDIAMETER'] = hole_size.LONGHOLEDIAMETER
    hole_size['PREV_HOLE_CROSS_SEC_AREA'] = np.power((hole_size.PREV_LONGHOLEDIAMETER/1000/2),2)*math.pi
    hole_size['CROSS_SEC_AREA_INCREASE_FROM_PREV_HOLE'] = hole_size.LONGHOLE_CROSS_SEC_AREA - hole_size.PREV_HOLE_CROSS_SEC_AREA
    hole_size['CROSS_SEC_AREA_INCREASE_RATIO'] = round(hole_size.CROSS_SEC_AREA_INCREASE_FROM_PREV_HOLE/hole_size.PILOT_HOLE_CROSS_SECTION_AREA,2)  ## this is compared to pilot hole
    hole_size['CROSS_SEC_AREA_INCREASE_RATIO'] = (hole_size.LONGHOLE_CROSS_SEC_AREA - hole_size.PREV_HOLE_CROSS_SEC_AREA)/hole_size.PREV_HOLE_CROSS_SEC_AREA + 1 ## this is compared to pilot hole
    hole_size['CROSS_SEC_AREA_INCREASE_RATIO'] = hole_size.CROSS_SEC_AREA_INCREASE_RATIO * np.sqrt(hole_size.groupby(['SITENAME','HOLE_ID']).CROSS_SEC_AREA_INCREASE_RATIO.shift().fillna(1))
    hole_size['TENDER_RATIO'] = (hole_size.LONGHOLE_CROSS_SEC_AREA - hole_size.PILOT_HOLE_CROSS_SECTION_AREA)/hole_size.PILOT_HOLE_CROSS_SECTION_AREA + 1

    hole_size['MIN_HOLE_SIZE'] = hole_size.groupby(['SITENAME','HOLE_ID']).LONGHOLEDIAMETER.transform('min')
    hole_size['MAX_HOLE_SIZE'] = hole_size.groupby(['SITENAME','HOLE_ID']).LONGHOLEDIAMETER.transform('max')
    hole_size['HOLE_TYPE'] = np.where(hole_size.MIN_HOLE_SIZE == hole_size.MAX_HOLE_SIZE, 'PROD', 'REAMER')

    ######## create groups of hole sizes
    conditions = [
        (hole_size.LONGHOLEDIAMETER.isin([64]))
        , (hole_size.LONGHOLEDIAMETER.isin([76,79]))
        , (hole_size.LONGHOLEDIAMETER.isin([89]))
        , (hole_size.LONGHOLEDIAMETER.isin([102]))
        , (hole_size.LONGHOLEDIAMETER.isin([110,115]))
        , (hole_size.LONGHOLEDIAMETER.isin([127]))
        , (hole_size.LONGHOLEDIAMETER.isin([152,157]))
        , (hole_size.LONGHOLEDIAMETER.isin([200,202,203,204,205]))
        , (hole_size.LONGHOLEDIAMETER >= 250)
        ]
    choices = [64,76,89,102,115,127,152,205,250]
    hole_size['HOLE_SIZE_GROUP'] = np.select(conditions, choices, default=89)


    lh_drill = pd.merge(lh_drill, hole_size[['SITENAME','HOLE_ID', 'LONGHOLEDIAMETER', 'HOLE_SIZE_GROUP','CROSS_SEC_AREA_INCREASE_RATIO', 'HOLE_TYPE']], how='left')
    lh_drill['EQUIV_LONGHOLEMETRES'] = round(lh_drill.LONGHOLEMETRES * lh_drill.CROSS_SEC_AREA_INCREASE_RATIO, 1)
    lh_drill.LONGHOLEDIAMETER = lh_drill.HOLE_SIZE_GROUP ## simplify the hole size and replace LONGHOLEDIAMETER with HOLE_SIZE_GROUP

    #####################################  create unique IDs for the Operators
    lh_drill['OPERATOR'] = lh_drill.groupby(['SITENAME']).OPERATORID.rank('dense').astype(int)

    #### To be added properly later
    lh_drill['COMMODITY_TYPE'] = 'ALL'
    return lh_drill


def operator_shiftly_data(lh_drill):
    lh_drill_op_shiftly = (
        lh_drill
        .assign(
            ACTUAL_METERS = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna())
            )
        .groupby(['SITENAME','DATE', 'MONTH', 'OPERATOR'],as_index=False).agg(
            LONGHOLEMETRES = ('ACTUAL_METERS',sum)
        )
    )
    ## an operator shift is considered a shift only if longhole drilling meters is greater than zero. Otherwise, don't consider it a shift and remove from shift data
    lh_drill_op_shiftly = lh_drill_op_shiftly.loc[lh_drill_op_shiftly.LONGHOLEMETRES > 0]

    lh_drill_op_monthly = lh_drill_op_shiftly.groupby(['SITENAME','OPERATOR','MONTH'], as_index=False).DATE.count()
    lh_drill_op_monthly = lh_drill_op_monthly.groupby(['SITENAME','OPERATOR'], as_index=False).DATE.mean()
    lh_drill_op_monthly.rename(columns={'DATE':'AVG_MONTHLY_OP_SHIFT_COUNT'}, inplace=True)
    lh_drill = pd.merge(lh_drill, lh_drill_op_monthly, on = ['SITENAME','OPERATOR'], how='left')
    return lh_drill


def data_quality(lh_drill):
    lh_drill_machine_shiftly = (
        lh_drill
        .assign(
            UP = lh_drill.LONGHOLEMETRES.where(lh_drill.UPDOWN == 'Up')
            , DOWN = lh_drill.LONGHOLEMETRES.where(lh_drill.UPDOWN == 'Down')
            , REAMING = lh_drill.LONGHOLEMETRES.where((lh_drill.HOLE_TYPE == 'REAMER') & (lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna()))
            , ACTUAL_METERS = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna())
            , HOLE_SIZE_METERS_64 = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna() & (lh_drill.HOLE_SIZE_GROUP == 64))
            , HOLE_SIZE_METERS_76 = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna() & (lh_drill.HOLE_SIZE_GROUP == 76))
            , HOLE_SIZE_METERS_89 = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna() & (lh_drill.HOLE_SIZE_GROUP == 89))
            , HOLE_SIZE_METERS_102 = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna() & (lh_drill.HOLE_SIZE_GROUP == 102))
            , HOLE_SIZE_METERS_LARGER_THAN_102 = lh_drill.LONGHOLEMETRES.where(lh_drill.CLEANING_METERS.isna() & lh_drill.MISC_METERS.isna() & (lh_drill.HOLE_SIZE_GROUP > 102))
            )
        .groupby(['SITENAME','COMMODITY_TYPE','DATE', 'MONTH','MACHINECODE','MACHINETYPE', 'SHIFT'],as_index=False).agg(
            LONGHOLEMETRES = ('ACTUAL_METERS',sum)
            , REAM_METERS = ('REAMING', sum)
            , UP_METERS = ('UP', sum)
            , DOWN_METERS = ('DOWN', sum)
            , HOLE_SIZE_METERS_64 = ('HOLE_SIZE_METERS_64', sum)
            , HOLE_SIZE_METERS_76 = ('HOLE_SIZE_METERS_76', sum)
            , HOLE_SIZE_METERS_89 = ('HOLE_SIZE_METERS_89', sum)
            , HOLE_SIZE_METERS_102 = ('HOLE_SIZE_METERS_102', sum)
            , HOLE_SIZE_METERS_LARGER_THAN_102 = ('HOLE_SIZE_METERS_LARGER_THAN_102', sum)
        ))

    ### remove any machine shifts that doesn't have any drill meters 
    lh_drill_machine_shiftly = lh_drill_machine_shiftly.loc[lh_drill_machine_shiftly.LONGHOLEMETRES > 0].reset_index(drop=True)
    lh_drill_machine_shiftly['HOLE_LARGER_THAN_102_METER_RATIO'] = np.where(lh_drill_machine_shiftly.LONGHOLEMETRES != 0, round(lh_drill_machine_shiftly.HOLE_SIZE_METERS_LARGER_THAN_102 / lh_drill_machine_shiftly.LONGHOLEMETRES, 2), np.nan)

    ############################### add only REAMING and only PROD SHIFTS
    lh_drill_machine_shiftly['PROD_METERS'] = lh_drill_machine_shiftly.LONGHOLEMETRES - lh_drill_machine_shiftly.REAM_METERS
    lh_drill_machine_shiftly['SHIFT_COUNT'] = 1 #this is used in daily, n-daily and monthly sum aggregations if needed. every row is a machine shift
    return lh_drill_machine_shiftly



def run_hours_data(lh_drill_machine_shiftly, machine_shiftly_hours, lh_drill):
    machine_shiftly_hours.columns = [x.upper() for x in machine_shiftly_hours.columns]
    machine_shiftly_hours['DATE'] = pd.to_datetime(machine_shiftly_hours['DATE'])
    machine_shiftly_hours['MONTH'] = machine_shiftly_hours['DATE'].dt.strftime('%Y-%m')

    ### sort value to ensure correct order
    machine_shiftly_hours.sort_values(['MACHINECODE','DATE','SHIFT'], ignore_index=True, inplace=True)

    machine_hours = machine_shiftly_hours.loc[(~machine_shiftly_hours.ENGINEHRS.isna() | ~machine_shiftly_hours.PERCUSSIONHRS.isna()) & machine_shiftly_hours.MACHINECODE.isin(lh_drill.MACHINECODE.drop_duplicates())]
    # merge percussion shiftly hours with longhole machline shiftly
    lh_drill_hours_machine_shiftly = pd.merge(  lh_drill_machine_shiftly, machine_hours,how='outer')
    lh_drill_hours_machine_shiftly.sort_values(['MACHINECODE','DATE','SHIFT'], ignore_index=True, inplace=True)

    ### Group rows so that all rows with either NA for engine hours or NA for percussion hours are grouped together with the first row below them where both engine hours and percussion hours are NOT NA
    lh_drill_hours_machine_shiftly['BOTH_ENGINE_AND_PERCUSS_EXIST'] = np.where(~lh_drill_hours_machine_shiftly.ENGINEHRS.isna() & ~lh_drill_hours_machine_shiftly.PERCUSSIONHRS.isna(),1,np.nan)
    lh_drill_hours_machine_shiftly['NA_PERCUSS_GROUP'] = lh_drill_hours_machine_shiftly.groupby(['SITENAME','MACHINECODE'], as_index = False).BOTH_ENGINE_AND_PERCUSS_EXIST.transform(create_na_group)

    ## remove anything with NA grouping because it means there is no hours data available
    lh_drill_hours_machine_shiftly = lh_drill_hours_machine_shiftly.loc[~lh_drill_hours_machine_shiftly.NA_PERCUSS_GROUP.isna()]
    lh_drill_hours_machine_shiftly.MACHINETYPE = lh_drill_hours_machine_shiftly.groupby('MACHINECODE').MACHINETYPE.ffill()  # first forward fill
    lh_drill_hours_machine_shiftly.MACHINETYPE = lh_drill_hours_machine_shiftly.groupby('MACHINECODE').MACHINETYPE.bfill()  # then back fill to make sure there are no NA

    ##############################################################
    lh_drill_hours_machine_shiftly_agg = lh_drill_hours_machine_shiftly.groupby(['SITENAME','COMMODITY_TYPE','MACHINECODE','MACHINETYPE','NA_PERCUSS_GROUP'], as_index=False).agg(
        DATE = ('DATE', 'last') 
        , MONTH = ('MONTH', 'last') 
        , SHIFT = ('SHIFT', 'last')
        , LONGHOLEMETRES = ('LONGHOLEMETRES', sum)
        , PERCUSSIONHRS = ('PERCUSSIONHRS', sum)
        , ENGINEHRS = ('ENGINEHRS', sum)
        , REAM_METERS = ('REAM_METERS', sum)
        , PROD_METERS = ('PROD_METERS', sum)
        , UP_METERS = ('UP_METERS', sum)
        , DOWN_METERS = ('DOWN_METERS', sum)
        , SHIFT_COUNT = ('LONGHOLEMETRES', lambda x: sum(~x.isna()))
    )

    lh_drill_hours_machine_shiftly_agg['RUNHRS'] =  lh_drill_hours_machine_shiftly_agg.ENGINEHRS + lh_drill_hours_machine_shiftly_agg.PERCUSSIONHRS
    lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT = np.where(lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT.isna() | (lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT == 0), 1, lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT)

    lh_drill_hours_machine_shiftly_agg['AVG_PERCUSSHRS_PER_SHIFT'] = round(lh_drill_hours_machine_shiftly_agg.PERCUSSIONHRS / lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT,2)
    lh_drill_hours_machine_shiftly_agg['AVG_METERS_PER_SHIFT'] = round(lh_drill_hours_machine_shiftly_agg.LONGHOLEMETRES / lh_drill_hours_machine_shiftly_agg.SHIFT_COUNT,2)

    ############### get rid of anomolies
    lh_drill_hours_machine_shiftly_agg['ANOM_PERCUSS_CLUSTER'] = lh_drill_hours_machine_shiftly_agg.groupby(['SITENAME','MACHINECODE']).AVG_PERCUSSHRS_PER_SHIFT.transform(lambda x: detect_outlier_dbscan(x, min_samples = 5, eps = 5))
    lh_drill_hours_machine_shiftly_agg['ANOM_METERS_CLUSTER'] = lh_drill_hours_machine_shiftly_agg.groupby(['SITENAME','MACHINECODE']).AVG_METERS_PER_SHIFT.transform(lambda x: detect_outlier_dbscan(x, min_samples = 5, eps = 5))

    lh_drill_hours_machine_shiftly_agg = lh_drill_hours_machine_shiftly_agg.loc[lh_drill_hours_machine_shiftly_agg.ANOM_PERCUSS_CLUSTER != -1].reset_index(drop=True)
    lh_drill_hours_machine_shiftly_agg = lh_drill_hours_machine_shiftly_agg.loc[lh_drill_hours_machine_shiftly_agg.AVG_PERCUSSHRS_PER_SHIFT < 12].reset_index(drop=True)
    lh_drill_hours_machine_shiftly_agg = lh_drill_hours_machine_shiftly_agg.loc[lh_drill_hours_machine_shiftly_agg.ANOM_METERS_CLUSTER != -1].reset_index(drop=True)
    return lh_drill_hours_machine_shiftly_agg


def penetration_rate_for_shiftly(lh_drill_hours_machine_shiftly_agg, lh_drill_machine_shiftly):
    rounding = 1
    lh_drill_hours_machine_shiftly_agg['PENETRATION_RATE'] = np.where(lh_drill_hours_machine_shiftly_agg.PERCUSSIONHRS != 0, round(lh_drill_hours_machine_shiftly_agg.LONGHOLEMETRES / lh_drill_hours_machine_shiftly_agg.PERCUSSIONHRS, rounding), np.nan)

    ############ make any ridiculous values that are outside three signma to NA
    lh_drill_hours_machine_shiftly_agg['THREE_SIGMA_VALUE'] = lh_drill_hours_machine_shiftly_agg.groupby('MACHINETYPE', as_index=False).PENETRATION_RATE.transform(lambda x: round(np.nanstd(x)*3, rounding))
    lh_drill_hours_machine_shiftly_agg.loc[lh_drill_hours_machine_shiftly_agg.PENETRATION_RATE >= lh_drill_hours_machine_shiftly_agg.THREE_SIGMA_VALUE, 'PENETRATION_RATE'] = np.nan


    ############ get average penetration rate for each site
    lh_drill_site_avg_penetrate = lh_drill_hours_machine_shiftly_agg.groupby(['SITENAME'], as_index=False).agg(
        AVG_SITE_PENETRATE= ('PENETRATION_RATE',lambda x: round(np.nanmean(x), rounding))
        )
    ### join average site penetration rate
    lh_drill_machine_shiftly = pd.merge(lh_drill_machine_shiftly, lh_drill_site_avg_penetrate, on=['SITENAME'], how='left')

    ############ get average penetration rate for each machine CODE
    lh_drill_machinecode_avg_penetrate = lh_drill_hours_machine_shiftly_agg.groupby(['MACHINECODE'], as_index=False).agg(
        AVG_MACHINECODE_PENETRATE= ('PENETRATION_RATE',lambda x: round(np.nanmean(x), rounding))
        )
    ### join average machine code penetration rate
    lh_drill_machine_shiftly = pd.merge(lh_drill_machine_shiftly, lh_drill_machinecode_avg_penetrate, on=['MACHINECODE'], how='left')

    ########### get average penetration rate for each machine TYPE
    lh_drill_machinemodel_avg_penetrate = lh_drill_hours_machine_shiftly_agg.groupby(['MACHINETYPE'], as_index=False).agg(
        AVG_MACHINETYPE_PENETRATE= ('PENETRATION_RATE',lambda x: round(np.nanmean(x), rounding))
        )

    ### join average machine model penetration rate
    lh_drill_machine_shiftly = pd.merge(lh_drill_machine_shiftly, lh_drill_machinemodel_avg_penetrate, on=['MACHINETYPE'], how='left')

    ########### join runhours_agg with machine shiftly data
    runhours_merge_cols = ['SITENAME','COMMODITY_TYPE','MACHINECODE','MACHINETYPE', 'DATE','MONTH','SHIFT']
    runhours_data_cols = ['PENETRATION_RATE']

    lh_drill_machine_shiftly = pd.merge(lh_drill_machine_shiftly, lh_drill_hours_machine_shiftly_agg[runhours_merge_cols + runhours_data_cols],on = runhours_merge_cols, how = 'left')
    lh_drill_machine_shiftly.sort_values(by=['MACHINECODE','DATE','SHIFT'], ignore_index=True, inplace=True) ## sort this to do backfill

    ###############################
    ## backfill missing penetration rate data
    lh_drill_machine_shiftly['PENETRATION_RATE'] = lh_drill_machine_shiftly.groupby(['SITENAME','MACHINECODE','MACHINETYPE']).PENETRATION_RATE.bfill()

    ## remove any 0 percusison hours for any row that has longhole meters larger than 0
    lh_drill_machine_shiftly.loc[(lh_drill_machine_shiftly.LONGHOLEMETRES > 0) & (lh_drill_machine_shiftly.PENETRATION_RATE == 0), 'PENETRATION_RATE'] = np.nan

    ## backfill missing aerage penetration rate data by site
    lh_drill_machine_shiftly['AVG_SITE_PENETRATE'] = lh_drill_machine_shiftly.groupby(['SITENAME']).AVG_SITE_PENETRATE.bfill()

    ## backfill missing aerage penetration rate data by machine code
    lh_drill_machine_shiftly['AVG_MACHINECODE_PENETRATE'] = lh_drill_machine_shiftly.groupby(['MACHINECODE']).AVG_MACHINECODE_PENETRATE.bfill()

    ## backfill missing aerage penetration rate data by machine model
    lh_drill_machine_shiftly['AVG_MACHINETYPE_PENETRATE'] = lh_drill_machine_shiftly.groupby(['MACHINETYPE']).AVG_MACHINETYPE_PENETRATE.bfill()

    ############## replace any NA penetration values with average of the machine code penetration value
    lh_drill_machine_shiftly.loc[lh_drill_machine_shiftly.PENETRATION_RATE.isna(), 'PENETRATION_RATE'] = lh_drill_machine_shiftly.AVG_MACHINECODE_PENETRATE

    ############## replace any NA penetration values with average of the machine type penetration value
    lh_drill_machine_shiftly.loc[lh_drill_machine_shiftly.PENETRATION_RATE.isna(), 'PENETRATION_RATE'] = lh_drill_machine_shiftly.AVG_MACHINETYPE_PENETRATE

    ##############################################################################
    lh_drill_machine_shiftly['PERCUSSHRS'] = np.where( lh_drill_machine_shiftly.PENETRATION_RATE != 0 
                                                    , round(lh_drill_machine_shiftly.LONGHOLEMETRES / lh_drill_machine_shiftly.PENETRATION_RATE,2)
                                                    , 0)
    return lh_drill_machine_shiftly