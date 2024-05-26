export const colourScheme: any= {
  Actual: "#4e79a7",
  LSTM: "#f28e2b",
  LSTM_low: "#e15759",
  LSTM_high: "#76b7b2",
};

export type LineData = Array<{
  id: string;
  data: Array<{
    x: number | string | Date;
    y: number | null;
  }>;
}>;

// functions to modify the json returns from backend to a format required for nivo charts
// im pretty sure these should be dynamic, but for the minute we good
export const transformLineData = (dfJSON: any): LineData => {
  return [
    {
      id: "LSTM_high",
      data: Object.entries(dfJSON.DATE).map(([k, v]) => ({
        x: new Date(v as number).toISOString().split("T")[0],
        y: dfJSON.LSTM_high[k],
      })),
    },
    {
      id: "LSTM_low",
      data: Object.entries(dfJSON.DATE).map(([k, v]) => ({
        x: new Date(v as number).toISOString().split("T")[0],
        y: dfJSON.LSTM_low[k],
      })),
    },
    {
      id: "LSTM",
      data: Object.entries(dfJSON.DATE).map(([k, v]) => ({
        x: new Date(v as number).toISOString().split("T")[0],
        y: dfJSON.LSTM[k],
      })),
    },
    {
      id: "Actual",
      data: Object.entries(dfJSON.DATE)
        .map(([k, v]) => ({
          x: new Date(v as number).toISOString().split("T")[0],
          y: dfJSON.actual[k],
        }))
        .filter(({ y }) => y !== null),
    },
  ];
};

// bar data next

export type BarData = Array<{
  date: string;
  LSTM: number;
  LSTM_low: number;
  LSTM_high: number;
  Actual: number;
}>;

export const transformBarData = (dfJSON: any): BarData => {
  const bd: BarData = [];
  const windowSize = 12;
  const dataLength = Object.keys(dfJSON.DATE).length;

  let pred_start = 0;
  
  while(dfJSON.LSTM[pred_start] === null)
    pred_start++;

  

  const actualValues: Array<number> = Object.values(dfJSON.actual);

  for (let i = pred_start; i < dataLength; i+=windowSize) {
    const date = new Date(dfJSON.DATE[i]).toISOString().split('T')[0];
    
    bd.push({
      date,
      LSTM: calculateRollingSum(dfJSON.LSTM, i, windowSize),
      LSTM_low: calculateRollingSum(dfJSON.LSTM_low, i, windowSize),
      LSTM_high: calculateRollingSum(dfJSON.LSTM_high, i, windowSize),
      Actual: calculateRollingSum(actualValues, i, windowSize),
    });
  }

  return bd;
};
// Helper function to calculate the rolling sum
const calculateRollingSum = (data: number[], index: number, windowSize: number): number => {
  if (index < windowSize - 1) {
    return 0;
  }

  let sum = 0;
  for (let i = index - windowSize + 1; i <= index; i++) {
    sum += data[i] || 0;
  }

  return sum;
};
