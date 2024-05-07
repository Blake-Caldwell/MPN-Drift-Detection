import numpy as np
import pandas as pd
import tsfresh

def forward_fill_averages(df_actuals: pd.DataFrame):
    """
    Forward fills the averages
    """
    try:
        df_actuals = df_actuals.groupby('DATE').sum(numeric_only=True).reset_index()

        last_monday_date = df_actuals.DATE.max() + relativedelta(weekday=MO(-1))
        last_monday_df = df_actuals[df_actuals.DATE >= last_monday_date]

        new_data = {}
        for column in df_actuals.columns:
            new_data[column] = last_monday_df[column].mean(numeric_only=True)
        new_data['DATE'] = df_actuals.DATE.max() + relativedelta(days=1)

        df_actuals = pd.concat([df_actuals, pd.DataFrame([new_data])], ignore_index=True, join='inner')
        df_actuals = df_actuals.set_index('DATE').resample('D').ffill().reset_index()

    except Exception as error:
        print("There is an error in forward_fill_averages")
    return df_actuals
    
def bogging_resampling(df, freq='W'):
    target_column = 'PRIMARY_TONNES'
    columns = ['DATE', 'TONNES', 'PRIMARY_TONNES', 'DEV_TONNES', 'PROD_TONNES', 'BF_TONNES', 'REHANDLE_TONNES', 'REMOTE_TONNES', 
               'STOPE_STOCKPILE_TONNES', 'STOCKPILE_TRUCK_TONNES', 'SHIFT_COUNT']
    df = df[columns]
    # df = forward_fill_averages(df)
    
    # Combine resampling and aggregation
    df = df.resample(freq, on='DATE').sum().reset_index()
    
    # Calculate ratios using vectorized operations
    ratio_columns = ['DEV_TONNES', 'PROD_TONNES', 'BF_TONNES', 'REHANDLE_TONNES', 'REMOTE_TONNES', 'STOPE_STOCKPILE_TONNES', 'STOCKPILE_TRUCK_TONNES']
    df[ratio_columns] = df[ratio_columns].div(df['TONNES'], axis=0)
    df[ratio_columns] = df[ratio_columns].round(2)
    
    return df, target_column


def lhdrilling_resampling(df, freq='W'):
    target_column = 'LONGHOLEMETRES'
    columns = ['DATE','LONGHOLEMETRES', 'PENETRATION_RATE', 'UP_METERS', 'REAM_METERS', 'HOLE_SIZE_METERS_64',
            'HOLE_SIZE_METERS_76', 'HOLE_SIZE_METERS_89', 'HOLE_SIZE_METERS_102', 'HOLE_SIZE_METERS_LARGER_THAN_102']
    df = df[columns]
    # df = forward_fill_averages(df)
    
    # Combine resampling and aggregation
    df = df.resample(freq, on='DATE').sum().reset_index()
    
    # Calculate ratios using vectorized operations
    ratio_columns = ['REAM_METERS', 'UP_METERS', 'HOLE_SIZE_METERS_64', 'HOLE_SIZE_METERS_76', 
                     'HOLE_SIZE_METERS_89', 'HOLE_SIZE_METERS_102', 'HOLE_SIZE_METERS_LARGER_THAN_102']
    df[ratio_columns] = df[ratio_columns].div(df['LONGHOLEMETRES'], axis=0)
    
    # Round ratios and replace NaN with np.nan
    df[ratio_columns] = df[ratio_columns].round(2)
    df[ratio_columns] = df[ratio_columns].where(df['LONGHOLEMETRES'] != 0, np.nan)
    
    return df, target_column


def trucking_resampling(df, freq='W'):
    target_column = 'TKM'
    columns = ['DATE', 'TKM', 'SHIFT_COUNT', 'TONNES', 'DISTANCE', 'LOADS']
    df = df[columns]
    
    # Combine resampling and aggregation
    df = df.resample(freq, on='DATE').agg({
        'TKM': 'sum',
        'TONNES': 'sum',
        'DISTANCE': 'sum',
        'LOADS': 'sum',
        'SHIFT_COUNT': 'sum'
    }).reset_index()
    
    # Calculate new columns using .loc
    df.loc[df.LOADS >= 1, 'TONNES_PER_LOAD'] = (df.TONNES / df.LOADS).round(1)
    df.loc[df.LOADS >= 1, 'DISTANCE_PER_LOAD'] = (df.DISTANCE / df.LOADS).round(1)
    
    # Drop unnecessary columns
    df.drop(['TONNES', 'LOADS', 'DISTANCE'], axis=1, inplace=True)
    
    return df, target_column

def unique_machinecodes(series):
    return list(set(series))


def jumbo_resampling(df, freq='W'):
    target_column = 'DRIVINGADVANCE'
    columns = ['DATE', 'DRIVINGADVANCE', 'FACEHOLES', 'FACEMETRES', 'MACHINE_SHIFTS', 'MACHINE_COUNT', 'SITE_CUT_ID',
               'MACHINE_LOCATION_CHANGE_PER_SHIFT', 'OPERATOR_COUNT', 'STRIPPINGMETRES', 'CUT_CALENDAR_SHIFTS',
               'DRILLSTEELLENGTH', 'HEADING_AREA', 'LOCS_LAST_7_DAYS', 'LOCS_NEXT_7_DAYS', 'UGLOCATIONID']
    df = df[columns]
    # df = forward_fill_averages(df)
    
    # Combine resampling and aggregation
    aggr_columns = ['DRIVINGADVANCE', 'FACEHOLES', 'FACEMETRES', 'MACHINE_SHIFTS', 'MACHINE_COUNT', 
                    'MACHINE_LOCATION_CHANGE_PER_SHIFT', 'OPERATOR_COUNT', 'STRIPPINGMETRES', 
                    'CUT_CALENDAR_SHIFTS']
    mean_columns = ['DRILLSTEELLENGTH', 'HEADING_AREA', 'LOCS_LAST_7_DAYS', 'LOCS_NEXT_7_DAYS']
    unique_columns = ['SITE_CUT_ID', 'UGLOCATIONID']
    df = df.resample(freq, on='DATE').agg({
        **{col: 'sum' for col in aggr_columns},
        **{col: 'mean' for col in mean_columns},
        **{col: 'nunique' for col in unique_columns}
    }).reset_index()
    
    return df, target_column


def get_tsfresh_features(df):
    df['id'] = (df.DATE.dt.week.diff() != 0).cumsum() - 1
    df_features = tsfresh.extract_features(df, column_id="id", column_sort='DATE', disable_progressbar=True)
    df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_features = df_features.dropna(axis=1)
    corr = df_features.corr()

    selected = []
    col_list = corr.columns
    removed = set()

    for i, col in enumerate(col_list):
        if col not in removed:
            num_cor = 0
            for j in range(i + 1, len(col_list)):
                if corr[col].iloc[j] > 0.85:
                    num_cor += 1
                    removed.add(col_list[j])
            if num_cor >= 5:
                selected.append(col)

    df_features = df_features[selected]
    return df_features


def add_date_features(df):
    df['month'] = df['DATE'].dt.month.astype(float)
    df['dayofmonth'] = df['DATE'].dt.day.astype(float)
    df['quarter'] = df['DATE'].dt.quarter.astype(float)
    df['dayofyear'] = df['DATE'].dt.day_of_year.astype(float)
    df['weekofyear'] = df['DATE'].dt.isocalendar().week.astype(float)
    return df

def read_parquet_files(folder_path):
    # List all files in the folder with a specific pattern
    parquet_files = [f for f in os.listdir(folder_path) if f.endswith('.snappy.parquet')]
    
    # Initialize an empty DataFrame to hold all data
    all_data = pd.DataFrame()
    
    # Iterate over the list of Parquet files and read each into a DataFrame
    for file in parquet_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_parquet(file_path)
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    # all_data now contains all data from the Parquet files
    return all_data

def preprocessing(input_path: str, save_path: str, activity: str, site_name: str, start_date, add_tsfresh_features):
    df = pd.read_csv(input_path)
    # df = read_parquet_files(input_path)
    df = df[(df['SITENAME'] == site_name) & (df['DATE'] >= start_date)].reset_index(drop=True)
    df['DATE'] = pd.to_datetime(df['DATE'])
    resampling = globals()[f'{activity}_resampling']

    if add_tsfresh_features:
        df_d, _ = resampling(df, freq='D')
        df_d = df_d.dropna()
        df_tsfresh = get_tsfresh_features(df_d)

    df, target_column = resampling(df)
    if add_tsfresh_features:
        df = pd.concat([df, df_tsfresh], axis=1)

    ### fill forward missed weeks
    df = df.reset_index(drop=True)[:-1]
    df.set_index('DATE', inplace=True)
    new_dates = pd.date_range(start=df.index[0], end=df.index[-1], freq='W')
    df = df.reindex(new_dates)
    df.fillna(method='ffill', inplace=True)
    df['DATE'] = df.index
    df.reset_index(inplace=True, drop=True)

    df = add_date_features(df)

    columns = ['DATE', target_column] + [col for col in df.columns if col not in ['DATE', target_column]]
    df = df[columns]
    df.to_csv(save_path, index=False)

    return df