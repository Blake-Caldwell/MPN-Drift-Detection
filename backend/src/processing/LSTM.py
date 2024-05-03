import pandas as pd
import pickle
import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

class LSTMModel(nn.Module):
    """
    Class that represents a Long Short Term Memory (LSTM) neural network model.
    """

    def __init__(self, input_dimension, hidden_dimension, number_of_layers, output_dimension):
        """
        Initialize the LSTM model.
        
        Args:
        input_dimension : int
                          The number of expected features in the input `x`
        hidden_dimension : int
                           The number of features in the hidden state `h`
        number_of_layers : int
                           Number of recurrent layers.
        output_dimension : int
                           The number of expected features in the output `x`
        """

        super(LSTMModel, self).__init__()

        # Store parameters
        self.hidden_dimension = hidden_dimension
        self.number_of_layers = number_of_layers

        # Define the LSTM layer
        self.lstm = nn.LSTM(input_dimension, hidden_dimension, number_of_layers, batch_first=True, dropout=0.4)

        # Define the output layer
        self.fc = nn.Linear(hidden_dimension, output_dimension)

    def forward(self, x):
        """
        Defines the computation performed at every call.

        Args:
        x : tensor
            The input tensor

        Returns:
        out : tensor
              The output tensor
        """

        # Initialize hidden state with zeros
        h0 = torch.zeros(self.number_of_layers, x.size(0), self.hidden_dimension).requires_grad_()

        # Initialize cell state
        c0 = torch.zeros(self.number_of_layers, x.size(0), self.hidden_dimension).requires_grad_()

        # Detach any gradients
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))

        # Pass the output tensor through the fully connected layer
        out = self.fc(out[:, -1, :]) 

        return out
    

class LSTMTimeseries:
    def __init__(self):
        pass

    def prepare_data(self, stock_data, sequence_length, label_col_name, prediction_length):
        """ 
        Function to prepare training and test datasets for time series prediction.

        Args:
        stock_data : pandas dataframe or series 
                    The stock prices dataset
        sequence_length : int 
                        The length of past sequence of data to be used for prediction
        
        Returns:
        [x_train, y_train, x_test, y_test] : list of numpy array 
                                            Split input and output, train and test data
        """

        # Initialize a list to store sequences of stock prices
        x_sequences = []
        y_sequences = []

        # Create all possible sequences of length sequence_length
        for i in range(len(stock_data) - prediction_length-sequence_length+1): 
            #print(i, i+sequence_length)
            #print(stock_data[i: i + sequence_length][-1])
            x_sequences.append(stock_data[i: i + sequence_length])
            y_sequences.append(stock_data[label_col_name][i + sequence_length: i + sequence_length+prediction_length])

        # Convert list of sequences into numpy array
        x_sequences_np = np.array(x_sequences)
        y_sequences_np = np.array(y_sequences)

        # Return the split data
        return [x_sequences_np, y_sequences_np]
    

    def train(
            self,
            df: pd.DataFrame,
            target_column: str,
            date_column: str,
            lookback: int,
            prediction_length: int,
            save_to: str = "lstm_timeseries.pkl",
            lr: float = 0.001,
            num_epochs: int = 100,
            hidden_dim : int= 32,
            num_layers: int = 2,
            feature_importance: bool = True,
    ):  
        x_train = df.copy(deep=True).drop(date_column, axis=1)

        # normalization
        for col_name in x_train.columns:
            if col_name != target_column:
                min_val = x_train[col_name].min()
                max_val = x_train[col_name].max()
                if max_val-min_val == 0:
                    x_train[col_name] = 0
                else:
                    x_train[col_name] = (((x_train[col_name]-min_val) / (max_val-min_val)) * 2) - 1
        min_val = x_train[target_column].min()
        max_val = x_train[target_column].max()
        x_train[target_column] = (((x_train[target_column]-min_val) / (max_val-min_val)) * 2) - 1

        x_forecast = np.expand_dims(x_train[-lookback:], axis=0)
        x_forecast = torch.from_numpy(x_forecast).type(torch.Tensor)
        x_train, y_train = self.prepare_data(x_train, lookback, target_column, prediction_length)
        #y_train = y_train.reshape(-1,1)

        x_train = torch.from_numpy(x_train).type(torch.Tensor)
        y_train_lstm = torch.from_numpy(y_train).type(torch.Tensor)

        input_dim = x_train.shape[2]
        output_dim = prediction_length

        model = LSTMModel(input_dimension=input_dim, hidden_dimension=hidden_dim, 
                          output_dimension=output_dim, number_of_layers=num_layers)
        criterion = torch.nn.MSELoss(reduction='mean')
        optimiser = torch.optim.Adam(model.parameters(), lr=lr)

        ### without batch data
        hist = np.zeros(num_epochs)
        for t in range(num_epochs):
            y_train_pred = model(x_train)

            loss = criterion(y_train_pred, y_train_lstm)
            #print("Epoch ", t, "MSE: ", loss.item())
            hist[t] = loss.item()

            optimiser.zero_grad()
            loss.backward()
            optimiser.step()

        if feature_importance:
            self.__feature_importance(model, x=x_train, y=y_train, 
                                      columns=df.columns[1:], 
                                      prediction_length=prediction_length)

        with open(save_to, "wb") as f:
            pickle.dump([model, x_forecast, min_val, max_val, prediction_length], f, pickle.HIGHEST_PROTOCOL)
        return hist
        

    def load_model(self,model_path: str,):
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)
        return model_data
    
    def predict(self,model_path,q1: float = 0.01,q2: float = 0.99):
        model_data = self.load_model(model_path)
        model, x_forecast, min_val, max_val, prediction_length = model_data

        # get lower and upper bound of LSTM prediction based on the method explained on the link below.
        # https://www.linkedin.com/pulse/time-series-forecasting-uncertainty-assessment-using-lstm-bohdan/
        prediction_list = np.zeros((prediction_length, 100))
        for j in range(100):
            # make predictions
            prediction = model(x_forecast)
            prediction = (((prediction.detach().numpy()+1)/2)*(max_val-min_val))+min_val
            prediction_list[:,j] = pd.Series(prediction[0])
        predictions = np.array(prediction_list)
    
        pred_df = pd.DataFrame()
        pred_df['pred'] = np.mean(predictions, axis=1)
        pred_df['pred_low'] = np.quantile(predictions, q1, axis=1)
        pred_df['pred_high'] = np.quantile(predictions, q2, axis=1)
        return pred_df
    
    """ def __feature_importance(
            self,
            model,
            x,
            y,
            columns,
            prediction_length,
    ):
        '''
        compute and show feature importance using a technique called Permutation Feature Importance.
        in this technique first a model is trained and then the columns are shuffled one by one to 
        see their effect on mae value.
        
        https://www.kaggle.com/code/cdeotte/lstm-feature-importance
        https://christophm.github.io/interpretable-ml-book/feature-importance.html#feature-importance
        
        '''

        x = np.copy(x)
        y = np.copy(y)
        results = []

        prediction_list = np.zeros((len(y), prediction_length, 100))
        for j in range(100):
            # make predictions
            prediction = model(torch.from_numpy(x).type(torch.Tensor))
            prediction = prediction.detach().numpy()
            prediction_list[:,:,j] = prediction
        predictions = np.array(prediction_list)
        pred = np.mean(predictions, axis=2)
        baseline_mae = np.mean(np.abs(pred - y))

        for k in tqdm(range(len(columns))):
            
            # SHUFFLE FEATURE K
            save_col = x[:,:,k].copy()
            np.random.shuffle(x[:,:,k])

            prediction_list = np.zeros((len(y), prediction_length, 100))
            for j in range(100):
                # make predictions
                prediction = model(torch.from_numpy(x).type(torch.Tensor))
                prediction = prediction.detach().numpy()
                prediction_list[:,:,j] = prediction
            predictions = np.array(prediction_list)
            pred = np.mean(predictions, axis=2)

            mae = np.mean(np.abs(pred - y))
            mae = max(mae - baseline_mae,0)
            results.append({'feature':columns[k],'mae':mae})
            x[:,:,k] = save_col
        
        df = pd.DataFrame(results)
        df = df.sort_values('mae')
        plt.figure(figsize=(5,10))
        plt.barh(np.arange(len(columns)),df.mae, color='blue')
        plt.yticks(np.arange(len(columns)),df.feature.values)
        plt.title('LSTM Feature Importance',size=16)
        plt.ylim((-1,len(columns)))
        plt.xlabel('MAE with feature permuted',size=14)
        plt.ylabel('Feature',size=14)
        plt.legend()
        plt.show()
         """
