import pandas as pd
import numpy as np


def jumbo_preprocessing(input_path:str, output_path:str):
    jumbo = pd.read_csv(input_path, low_memory=False)
    jumbo.columns = [x.upper() for x in jumbo.columns]
    jumbo['DATE'] = pd.to_datetime(jumbo['DATE'])

    jumbo = data_quality_check_and_fix(jumbo)
    jumbo_site_cutly = site_cutly_data(jumbo)
    jumbo_site_cutly = add_last_and_next_7days(jumbo_site_cutly)
    jumbo_site_cutly.rename(columns={'CUT_END_DATE':'DATE'}, inplace=True)
    jumbo_site_cutly.to_csv(output_path, index=False)



def data_quality_check_and_fix(jumbo):
    ########## clean up heading size based on heading height
    jumbo['HEADING_SIZE']= jumbo.HEADINGSIZE.str.findall(r'(\d+(?:\.\d+)?)')
    jumbo['HEADING_SIZE1']= pd.to_numeric(jumbo.HEADING_SIZE.str[0], errors='coerce')
    jumbo['HEADING_SIZE2']= pd.to_numeric(jumbo.HEADING_SIZE.str[1], errors='coerce')
    jumbo['H1_2'] = jumbo.HEADING_SIZE1.astype(str) + ' m x ' + jumbo.HEADING_SIZE2.astype(str) + ' m'
    jumbo['H2_1'] = jumbo.HEADING_SIZE2.astype(str) + ' m x ' + jumbo.HEADING_SIZE1.astype(str) + ' m'
    jumbo.HEADINGSIZE = np.where( (jumbo.HEADINGHEIGHT == jumbo.HEADING_SIZE2) | (jumbo.HEADINGHEIGHT == 0) | (jumbo.HEADINGHEIGHT.isna())
                                    , jumbo.H1_2
                                    , jumbo.H2_1
                                    )
    jumbo.drop(['HEADING_SIZE','HEADING_SIZE1','HEADING_SIZE2','H1_2','H2_1'], axis=1, inplace=True) ## remove added columns

    ## convert string to date
    # jumbo['DATE'] = (pd.to_datetime(jumbo['RECDATE'], format="%d/%m/%Y"))
    jumbo['DATE2'] = jumbo.DATE.dt.strftime('%Y-%m-%d')
    jumbo['MONTH'] = jumbo.DATE.dt.strftime('%Y-%m')
    jumbo['SHIFT_NUM'] = np.where(jumbo.SHIFT == 'Day', 1, 2)

    #####################################  create unique IDs for the Operators
    jumbo['OPERATOR'] = jumbo.groupby(['SITENAME']).OPERATORID.rank('dense').astype(int)

    #################################### creaute unique IDs for each cut at a location per site minesite
    jumbo.sort_values(by=['SITENAME','DATE', 'SHIFT','MACHINECODE'], ignore_index=True, inplace=True)
    jumbo['DRIVING_CUT']=np.where(jumbo.DRIVINGCUTS > 0, 1, np.nan)
    jumbo['SITE_CUT_ID'] = jumbo.groupby(['SITENAME']).DRIVING_CUT.cumsum()
    jumbo['SITE_CUT_ID'] = jumbo.groupby(['SITENAME','UGLOCATIONID']).SITE_CUT_ID.ffill() # first forward fill
    jumbo['SITE_CUT_ID'] = jumbo.groupby(['SITENAME','UGLOCATIONID']).SITE_CUT_ID.bfill() # then backward fill

    ################################### create proxy variables
    jumbo['HEADING_AREA'] = np.where(jumbo.DRIVINGADVANCERECONCILED != 0 , round(jumbo.DRIVINGM3 / jumbo.DRIVINGADVANCERECONCILED,1), np.nan)
    jumbo.DRIVINGCUTS = np.where((jumbo.DRIVINGADVANCERECONCILED == 0) & (jumbo.DRIVINGADVANCE > 0)
                                , 0 , jumbo.DRIVINGCUTS)
    return jumbo


def site_cutly_data(jumbo):
    ################# First Get machine shiftly data
    jumbo['PREV_UGLOCATIONID'] = jumbo.groupby(['SITENAME','DATE','SHIFT', 'MACHINECODE'], as_index=False).UGLOCATIONID.shift(1) 
    jumbo['MACHINE_LOCATION_CHANGE_PER_SHIFT'] = (jumbo.UGLOCATIONID != jumbo.PREV_UGLOCATIONID) + 0
    jumbo.MACHINE_LOCATION_CHANGE_PER_SHIFT = np.where(jumbo.PREV_UGLOCATIONID.isna(), 0, jumbo.MACHINE_LOCATION_CHANGE_PER_SHIFT)

    ######################################################
    jumbo_site_cutly = (
        jumbo
        # .assign(
        #     )
        .groupby(['SITENAME','SITE_CUT_ID'],as_index=False).agg(
            UGLOCATIONID = ('UGLOCATIONID', 'first')
            , DRILLSTEELLENGTH = ('DRILLSTEELLENGTH', max)
            , FACEHOLES = ('FACEHOLES', sum)
            , FACEMETRES = ('FACEMETRES', sum)  
            , DRIVINGADVANCE = ('DRIVINGADVANCERECONCILED',sum)
            , HEADING_AREA = ("HEADING_AREA", lambda x : np.nanmax(x))
            , HEADING_HEIGHT = ("HEADINGHEIGHT", lambda x : np.nanmax(x))  
            , MACHINE_SHIFTS = ('DRIVINGADVANCERECONCILED', 'count')
            , MACHINE_COUNT = ('MACHINECODE', 'nunique')
            , MACHINE_LOCATION_CHANGE_PER_SHIFT = ('MACHINE_LOCATION_CHANGE_PER_SHIFT', sum)
            # , MACHINE_SHIFT_COUNT_WITH_LOCATION_CHANGE = ('MACHINE_LOCATION_CHANGE_PER_SHIFT', lambda x: sum(x>0))
            , OPERATOR_COUNT = ('OPERATORID', 'nunique')
            , DRIVINGM3 = ('DRIVINGM3',sum)
            , TOTALHOLESFIRED = ('TOTALHOLESFIRED',sum)
            , STRIPPINGMETRES = ('STRIPPINGMETRES', sum)
            , STRIPPINGHOLES = ('STRIPPINGHOLES', sum)
        )
    )

    ################## get the number of calender shifts from the start of the cut to the end
    cut_shifts = jumbo[['SITENAME','SITE_CUT_ID','DATE','SHIFT']].sort_values(['DATE']).groupby(['SITENAME','SITE_CUT_ID'])
    cut_shifts = cut_shifts.nth(0).merge(cut_shifts.nth(-1), on=['SITENAME','SITE_CUT_ID'], suffixes=['_min', '_max']).reset_index(drop=True)
    cut_shifts.columns = ['SITENAME', 'SITE_CUT_ID', 'CUT_START_DATE', 'CUT_START_SHIFT', 'CUT_END_DATE', 'CUT_END_SHIFT']
    cut_shifts.CUT_START_SHIFT = np.where(cut_shifts.CUT_START_SHIFT == 'Day', 1, 2)
    cut_shifts.CUT_END_SHIFT = np.where(cut_shifts.CUT_END_SHIFT == 'Day', 1, 2)
    cut_shifts['SHIFT_DIFF'] = cut_shifts.CUT_END_SHIFT - cut_shifts.CUT_START_SHIFT
    cut_shifts['DATE_DIFF'] = cut_shifts.CUT_END_DATE - cut_shifts.CUT_START_DATE
    cut_shifts.DATE_DIFF = cut_shifts.DATE_DIFF.dt.days
    cut_shifts['CUT_CALENDAR_SHIFTS'] = cut_shifts.DATE_DIFF*2 + cut_shifts.SHIFT_DIFF + 1
    cut_shifts.CUT_START_SHIFT = np.where(cut_shifts.CUT_START_SHIFT == 1, 'Day', 'Night')
    cut_shifts.CUT_END_SHIFT = np.where(cut_shifts.CUT_END_SHIFT == 1, 'Day', 'Night')

    ## merge with cutly data
    jumbo_site_cutly = pd.merge(jumbo_site_cutly, cut_shifts[['SITENAME','SITE_CUT_ID','CUT_START_DATE','CUT_START_SHIFT','CUT_END_DATE','CUT_END_SHIFT' ,'CUT_CALENDAR_SHIFTS']], on=['SITENAME','SITE_CUT_ID'], how='left')
    return jumbo_site_cutly


def add_last_and_next_7days(jumbo_site_cutly):
    ########################################  get the unique UGLOCATIONID in the last 7 and the next 7 days for each cut
    days = {'n1': 7}

    ### last 7 days
    jumbo_site_cutly = jumbo_site_cutly.sort_values(by=['SITENAME', 'CUT_START_DATE'], ascending=[True,True]) ## somehow this sorting is required in order for rolling to work otherwise error is produced
    jumbo_site_cutly = jumbo_site_cutly.join(pd.concat([
            (pd.Series(pd.factorize(jumbo_site_cutly['UGLOCATIONID'])[0],
                        index=jumbo_site_cutly['CUT_START_DATE'])
                .groupby(jumbo_site_cutly['SITENAME'].values)
                .rolling(f'{v}D')
                .apply(lambda x: x.nunique()).to_frame(name=f'LOCS_LAST_{v}_DAYS')
                ) for k, v in days.items()], axis=1)
                .set_axis(jumbo_site_cutly.index)
                )

    ### next 7 days
    jumbo_site_cutly = jumbo_site_cutly.sort_values(by=['SITENAME', 'CUT_START_DATE'], ascending=[True,False]) ## somehow this sorting is required in order for rolling to work otherwise error is produced
    jumbo_site_cutly = jumbo_site_cutly.join(pd.concat([
            (pd.Series(pd.factorize(jumbo_site_cutly['UGLOCATIONID'])[0],
                        index=jumbo_site_cutly['CUT_START_DATE'])
                .groupby(jumbo_site_cutly['SITENAME'].values)
                .rolling(f'{v}D')
                .apply(lambda x: x.nunique()).to_frame(name=f'LOCS_NEXT_{v}_DAYS')
                ) for k, v in days.items()], axis=1)
                .set_axis(jumbo_site_cutly.index)
                )

    jumbo_site_cutly.sort_values(by=['SITENAME', 'SITE_CUT_ID'], ascending=[True,True], inplace=True)
    return jumbo_site_cutly
