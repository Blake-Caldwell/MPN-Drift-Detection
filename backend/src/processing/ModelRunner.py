import pandas as pd
import os
#import multiprocessing

from src.processing.LSTM import *

class ModelRunner:
    def train_model(
        self,
        df,
        target_column,
        activity,
        site_name,
        num_test_prediction,
        date_column,
        new_dates_prediction,
        forecast_length,
        freq,
        input_chunk_length,
    ):
        total_pred_df = pd.DataFrame()
        # models_name = set()
        for i in range(not new_dates_prediction, num_test_prediction+1):
            print(
                f'{i+1} Backtest period, {20 * "+"} LSTM model for {activity.upper()} in {site_name.upper()} Site {20 * "+"}'
            )

            #### train and test split ###
            train_idx_max = None if i == 0 else -i * forecast_length
            train_df = df[:train_idx_max]
            train_df = train_df[train_df[date_column] <= train_df[date_column].iloc[-1]]

            ### make target smoother, in this case, alpha=0.4 means that more weight is given to more recent observations.
            train_df[target_column] = train_df[target_column].ewm(alpha=0.4).mean()

            # define test date
            test_dates = pd.date_range(
                start=train_df[date_column].iloc[-1],
                periods=forecast_length + 1,
                freq=freq,
            )[1:]
            test_dates = pd.DataFrame({date_column: test_dates})
            pred_df = pd.DataFrame({date_column: test_dates[date_column]})

            ### LSTM train and prediction
            feature_importance = False  # True if i == num_test_prediction else False
            lstm = LSTMTimeseries()
            _ = lstm.train(
                train_df.copy(deep=True),
                target_column=target_column,
                date_column=date_column,
                lookback=input_chunk_length,
                prediction_length=forecast_length,
                save_to=f"src/models/lstm_{site_name}_{activity}.pkl",
                num_epochs=1068,
                lr=0.00595,
                num_layers=2,
                hidden_dim=43,
                feature_importance=feature_importance,
            )
            lstm_preds = lstm.predict(
                model_path=f"src/models/lstm_{site_name}_{activity}.pkl"
            )
            pred_df["LSTM"] = lstm_preds["pred"]
            pred_df["LSTM_low"] = lstm_preds["pred_low"]
            pred_df["LSTM_high"] = lstm_preds["pred_high"]
            # models_name.add('LSTM')

            # concatenate predictions
            if len(total_pred_df) == 0:
                for col_name in pred_df.keys():
                    total_pred_df[col_name] = []
            total_pred_df = pd.concat([pred_df, total_pred_df])

        total_pred_df = total_pred_df.reset_index(drop=True)

        print(total_pred_df)

        return total_pred_df

    def run_model(self, job: dict):
        # make folder for storing generated models if it doesn't exist
        os.makedirs("src/models", exist_ok=True)

        # can be removed
        # clears previous models to prevent the folder from overflowing
        for file_name in os.listdir("src/models"):
           if file_name.endswith(".pkl"):
                os.remove("src/models/"+file_name)

        # set up multiprocessing
        # pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)

        config = job["config"]

        site_name = job["site_name"]

        # read config for values used for running models
        num_test_prediction = config["num_test_prediction"]
        new_dates_prediction = config["new_dates_prediction"]
        forecast_length = config["forecast_length"]
        freq = config["freq"]
        input_chunk_length = config["input_chunk_length"]
        date_column = config["date_column"]

        for activity in job["result"]:
            df = job["result"][activity]["data_frame"]
            target_column = job["result"][activity]["target_column"]
            df[date_column] = pd.to_datetime(df[date_column])

            job["result"][activity]["pred_data_frame"] = self.train_model(
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
            )   

        return job

            # train each model asynchronously
            # job["result"][activity]["pred_data_frame"] = pool.apply_async(
            #     self.train_model,
            #     args=(
            #         df,
            #         target_column,
            #         activity,
            #         site_name,
            #         num_test_prediction,
            #         date_column,
            #         new_dates_prediction,
            #         forecast_length,
            #         freq,
            #         input_chunk_length,
            #     ),
            # )

        # finish asynchronous processing
        #pool.close()
        #pool.join()

        # get result from all async objects
        #for activity in job["result"]:
        #    job["result"][activity]["pred_data_frame"] = job["result"][activity][
        #        "pred_data_frame"
        #    ].get()
