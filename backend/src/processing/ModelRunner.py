import pandas as pd
import os
import multiprocessing

from src.processing.LSTM import *

#   Author: Abigail Cummins
#   Date: 06/05/24
#
#   Version: 2
#   - Addition of multiprocessing when running models
#
#   Version: 3
#   - Modification to handle Job (Dict{"job_id": ,Dict{"status": , "result": , "config": }}structures and config files

# ModelRunner Class
    #
    # Prerequisites: The CSV files would have been loaded into dataframes, preprocessed using the values in the
    #   config file and would be stored a dataframes ready to be put into the LSTM model. The configs necessary
    #   for the running of the model would also be provided or have access to somehow (such as the target value)
    #
    # runModel():
    # 1: Run each activity for all the mines asynchronously (all dataframes that are received) using the LSTM model
    #   - This would use Mehdi's code, specifically the train_models function in Mehdi's notebook
    #   - All dataframes are presumed to have been preprocessed already using preprocessing.py from Mehdi's code
    #   2: Set the date column using pandas to_datetime
    #   3: Run train_models (only runs the LSTM model)
    #       - This will generate pickle files for each model generated after LSTM training
    #       - This pickle file is then used to generate the prediction dataframe
    #       - These pickle files are saved under backend/src/models for saving if a particularly good model is made
    #       - Each time this is run the pickle file will be overridden
    # 4: Return prediction results object after all models have finished
    #   - These results will be in the structure of a dictionary (dict) or a name (string) and the prediction dataframe
    #   - The structure for the name in the dict could be {siteName_activity}
    #   - These results can organised and encapsulated etc. and plotted at the front end
    #
    # TODO:
    #   - Add unit testing
    #   - Finish comments and internal documentation
    #   - Fix the FutureWarning caused by concat on empty dataframes

class ModelRunner():    
    def train_model(self, df, target_column, activity, site_name, num_test_prediction, date_column, new_dates_prediction,forecast_length,freq,input_chunk_length):
        total_pred_df = pd.DataFrame()
        #models_name = set()
        for i in range(not new_dates_prediction, num_test_prediction):
            print(f'{i+1} Backtest period, {20 * "+"} LSTM model for {activity.upper()} in {site_name.upper()} Site {20 * "+"}')

            #### train and test split ###
            train_idx_max = None if i == 0 else -i*forecast_length
            train_df = df[:train_idx_max]
            train_df = train_df[train_df[date_column] <= train_df[date_column].iloc[-1]]

            ### make target smoother, in this case, alpha=0.4 means that more weight is given to more recent observations.
            train_df[target_column] = train_df[target_column].ewm(alpha=0.4).mean()

            # define test date
            test_dates = pd.date_range(start=train_df[date_column].iloc[-1], periods=forecast_length+1, freq=freq)[1:]
            test_dates = pd.DataFrame({date_column:test_dates})
            pred_df = pd.DataFrame({date_column:test_dates[date_column]})

            ### LSTM train and prediction
            feature_importance = False #True if i == num_test_prediction else False
            lstm = LSTMTimeseries()
            _ = lstm.train(train_df.copy(deep=True), target_column=target_column, date_column=date_column,
                            lookback=input_chunk_length, prediction_length=forecast_length, 
                            save_to=f'backend/src/models/lstm_{site_name}_{activity}.pkl', num_epochs=1068, lr=0.00595,
                            num_layers=2, hidden_dim=43, feature_importance=feature_importance)
            lstm_preds = lstm.predict(model_path=f'backend/src/models/lstm_{site_name}_{activity}.pkl')
            pred_df['LSTM'] = lstm_preds['pred']
            pred_df['LSTM_low'] = lstm_preds['pred_low']
            pred_df['LSTM_high'] = lstm_preds['pred_high']
            #models_name.add('LSTM')

            # concatenate predictions
            if len(total_pred_df) == 0:
                for col_name in pred_df.keys():
                    total_pred_df[col_name] = []
            total_pred_df = pd.concat([pred_df, total_pred_df])

        total_pred_df = total_pred_df.reset_index(drop=True)

        return total_pred_df
    
    def run_model(self,job: dict):
        #make folder for storing generated models if it doesn't exist
        os.makedirs("backend/src/models", exist_ok=True)

        #set up multiprocessing
        pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())

        config = job['config']

        site_name = job['site_name']

        #read config for values used for running models
        num_test_prediction = config['num_test_prediction']
        new_dates_prediction = config['new_dates_prediction']
        forecast_length = config['forecast_length']
        freq = config['freq']
        input_chunk_length = config['input_chunk_length']
        date_column = config['date_column']

        for activity in job['result']: 
            df = job['result'][activity]['data_frame']
            target_column = job['result'][activity]['target_column']
            df[date_column] = pd.to_datetime(df[date_column])

            #train each model asynchronously
            job['result'][activity]['pred_data_frame'] = pool.apply_async(self.train_model,args=(
                df, 
                target_column, 
                activity, 
                site_name, 
                num_test_prediction, 
                date_column, 
                new_dates_prediction,
                forecast_length,
                freq,
                input_chunk_length
                ))
        
        #finish asynchronous processing
        pool.close()
        pool.join()

        #get result from all async objects
        for activity in job['result']: 
            job['result'][activity]['pred_data_frame'] = job['result'][activity]['pred_data_frame'].get()

        #return job
    