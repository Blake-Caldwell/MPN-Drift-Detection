import Serie from '@nivo/line'

export type LineData = Array<{
  id: string;
  data: Array<{
    x: number | string | Date;
    y: number | null;
  }>;
}>;


// functions to modify the json returns to a format required for nivo charts
// im pretty sure these should be dynamic, but for the minute we good
export const transformLineData = (dfJSON: any): LineData =>  {

    return [
        {
          "id": "LSTM",
          "data": Object.entries(dfJSON.DATE).map(([k, v]) => ({
            "x": new Date(v as number).toISOString().split('T')[0],
            "y": dfJSON.LSTM[k]
          }))
        },
        {
          "id": "LSTM_low",
          "data": Object.entries(dfJSON.DATE).map(([k, v]) => ({
            "x": new Date(v as number).toISOString().split('T')[0],
            "y": dfJSON.LSTM_low[k]
          }))
        },
        {
          "id": "LSTM_high",
          "data": Object.entries(dfJSON.DATE).map(([k, v]) => ({
            "x": new Date(v as number).toISOString().split('T')[0],
            "y": dfJSON.LSTM_high[k]
          }))
        },
        {
          "id": "actual",
          "data": Object.entries(dfJSON.DATE).map(([k, v]) => ({
            "x": new Date(v as number).toISOString().split('T')[0],
            "y": dfJSON.actual[k]
          })).filter(({ y }) => y !== null)
        }
      ];
}

// bar data next