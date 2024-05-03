import pandas as pd
import os
from LSTM import *

#Temp for testing once config and preprocessing is finished

freq = 'W'
""" The default frequency for the forecast model """

date_column = 'DATE'
""" The date column for the model """

input_chunk_length = 12
""" The length of the input chunks, required for the forecast model """

forecast_length = 12
""" The default forecast length for the model """

targets = {
    "jumbo": "DRIVINGADVANCE",
    "bogging": "PRIMARY_TONNES",
    "lhdrilling": "LONGHOLEMETRES",
    "trucking": "TKM",
    "trucking_surface_ore": "ORE_TONNES_TO_SURFACE",
}
""" The target columns required by the model """

new_dates_prediction = True

num_test_prediction = 5
""" Backtesting Period Count """

site_name = 'Idobamine'
""" Mine site name """

activity_list = ['trucking', 'bogging', 'jumbo', 'lhdrilling']
""" All activities in the MPN model """

start_date='2021-01-01'

#   WIP
#   Author: Abigail Cummins
#   Date: 03/05/24
#   Version: 1

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
    #   - Asynchronous processing
    #   - Integration into the Results and DataProcessing classes
    #   - Missing additions to requirements.txt for the LSTM
    #   - Add unit testing

class ModelRunner():    
    #to change
    def __init__(self):
        self._models = []

    @property
    def models(self):
        return self._models
    
    @models.setter
    def models(self, m):
        self._models = m

    def addModel(self,newModel):
        self._models.append(newModel)
    #to change

    def train_models(self, df, target_column, activity, site_name, num_test_prediction):
        total_pred_df = pd.DataFrame()
        #models_name = set()
        for i in range(not new_dates_prediction, num_test_prediction+1):
            #logging.info(f'{i+1} Backtest period, {20 * "+"} LSTM model for {activity.upper()} in {site_name.upper()} Site {20 * "+"}')

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

        #models_name = list(models_name)

        return total_pred_df#, models_name

    #temp for testing 
    def runModel(self):
        results = []

        #make folder for storing models
        os.makedirs("backend/src/models", exist_ok=True)

        for activity in activity_list:
            print("starting "+activity) 
            target_column = targets[activity]
            
            #hardcoded for testing purposes
            df = pd.read_csv(rf"C:\Users\jonah\OneDrive\Desktop\Uni\2024 S1\ICT302\MPN_forecasring_backtest\preprocessed_data\preprocessed_{site_name}_{activity}.csv")
            
            results.append(self.train_models(df, target_column, activity, site_name, num_test_prediction))
            print("finished "+activity)
        return results
