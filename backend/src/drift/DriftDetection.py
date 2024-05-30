'''import pandas as pd

class DriftDetection:
    def detect_drift(self,df,target_column,date_column):
        # Ensure the date column is in datetime format
        df[date_column] = pd.to_datetime(df[date_column])

        # Drop rows where the target column has NaN values
        df = df.dropna(subset=[target_column])

        # Set the date column as the index
        df.set_index(date_column, inplace=True)

        # Calculate the monthly median of the target column
        monthly_median = df[target_column].resample('ME').median()
        #monthly_median = df['LSTM'].resample('ME').median()

        # Remove months where the median is NaN after resampling
        monthly_median = monthly_median.dropna()

        # Calculate the gradient of monthly medians
        gradient = monthly_median.diff()

        # Drop NaN values in the gradient to avoid impact in downstream analysis
        gradient = gradient.dropna()

        # Calculate the left rolling average of the gradients over a three-month period
        rolling_average = gradient.rolling(window=3, min_periods=1).mean()

        # Shift the rolling average down by one period to match the current month with the previous month's data
        shifted_rolling_average = rolling_average.shift(1)

        # Drop NaN values in the shifted rolling average to ensure clean data for analysis
        shifted_rolling_average = shifted_rolling_average.dropna()

        # Calculate the absolute difference between the gradient and the shifted rolling average
        difference = abs(gradient - shifted_rolling_average)

        # Standardise the differences using z-score
        difference_z_score = (difference - difference.mean()) / difference.std()

        # Define a threshold for detecting significant drift in z-score terms
        #changed to 2 for testing
        z_threshold = 1.00

        # Determine if there is a significant drift
        drift_detected = (difference_z_score > z_threshold).any()

        drift_status = {}

        # Print message if drift is detected
        if drift_detected:
            #print(f"Drift detected in {target_column}. Drift points (Date, Difference, Z-Score):")
            drift_points = difference[difference_z_score > z_threshold]
            
            # If drift points are found, then iterate over them and print
            if not drift_points.empty:
                for date, diff in drift_points.items():
                    z_score = difference_z_score[date]
                    #print(f"date: {date}, difference: {diff:.4f}, z_score: {z_score:.4f}, activity: {activity}")
                    drift_status[date] = {"status": "Significant", "difference": f"{diff:.4f}", "z_score": f"{z_score:.4f}"}
                    
            else:
                #print(f"No significant drift points found above the threshold in {target_column}")
                drift_status = {"date": "not-significant"}
            
        else:
            #print(f"No drift detected in {target_column}")
            drift_status = {"date": "none"}


        
        
        

        return drift_status
'''


import pandas as pd

class DriftDetection:
    def detect_drift(self, df, target_column, date_column):
        
        # Ensure the date column is in datetime format
        df[date_column] = pd.to_datetime(df[date_column])

        # Drop rows where the target column has NaN values
        df = df.dropna(subset=[target_column])

        # Set the date column as the index
        df.set_index(date_column, inplace=True)

        # Get the max date in the dataset
        max_date = df.index.max()

        # Filter the df to include only dates up to the maximum date
        df = df[df.index <= max_date]

        # Calculate the monthly median of the target column
        monthly_median = df[target_column].resample('ME').median()

        # Remove months where the median is NaN after resampling
        monthly_median = monthly_median.dropna()

        # Calculate the gradient of monthly medians
        gradient = monthly_median.diff()

        # Drop NaN values in the gradient to avoid impact in downstream analysis
        gradient = gradient.dropna()

        # Calculate the left rolling average of the gradients over a three-month period
        rolling_average = gradient.rolling(window=3, min_periods=1).mean()

        # Shift the rolling average down by one period to match the current month with the previous month's data
        shifted_rolling_average = rolling_average.shift(1)

        # Drop NaN values in the shifted rolling average to ensure clean data for analysis
        shifted_rolling_average = shifted_rolling_average.dropna()

        # Calculate the absolute difference between the gradient and the shifted rolling average
        difference = abs(gradient - shifted_rolling_average)

        # Standardise the differences using z-score
        difference_z_score = (difference - difference.mean()) / difference.std()

        # Define a threshold for detecting significant drift in z-score terms
        z_threshold = 1.00  # Change to 2 for testing

        # Determine if there is a significant drift
        drift_detected = (difference_z_score > z_threshold).any()

        drift_status = {}

        # Print message if drift is detected
        if drift_detected:
            drift_points = difference[difference_z_score > z_threshold]

            # If drift points are found, then iterate over them and print
            if not drift_points.empty:
                for date, diff in drift_points.items():
                    z_score = difference_z_score[date]
                    drift_status[date] = {"status": "Significant", "difference": f"{diff:.4f}", "z_score": f"{z_score:.4f}"}
            else:
                drift_status = {"date": "not-significant"}
        else:
            drift_status = {"date": "none"}

        return drift_status



# Example usage:
'''for activity in activity_list:
    input_path = f"{input_folder}/mpn_{site_name}_{activity}.csv"
    df = pd.read_csv(input_path)
    target_column = targets[activity]
    date_column = 'DATE'  
    detect_drift(df, target_column, date_column)'''
