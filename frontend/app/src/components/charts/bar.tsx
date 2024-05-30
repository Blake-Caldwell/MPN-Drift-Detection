import { ResponsiveBar } from '@nivo/bar';
import { BarData, colourScheme } from '@/utils/chartUtils';

type BarChartProps = {
  data: BarData;
  target: string;
};

export const BarChart = ({ data, target }: BarChartProps) => {
  const keys = ["Actual", "LSTM", 
  "LSTM_low", "LSTM_high"
];


  return (
    <ResponsiveBar
      data={data}
      keys={keys}
      indexBy="date"
      margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
      padding={0.3}
      innerPadding={3}
      groupMode="grouped"
      valueScale={{ type: 'linear' }}
      indexScale={{ type: 'band', round: true }}
      colors={({ id }) => colourScheme[id]}
      borderWidth={2}
      borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
      axisTop={null}
      axisRight={null}
      axisBottom={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: '12 Week Groups',
        legendPosition: 'middle',
        legendOffset: 32,
      }}
      axisLeft={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: target,
        legendPosition: 'middle',
        legendOffset: -50,
        format: (value) => {
            if(value > 10000)
            {
              return `${value / 1000}K`
            }
            return `${value}`
        }
      }}
      enableLabel={false}
      //label={d => `${d.value/1000}K`}
      labelSkipWidth={12}
      labelSkipHeight={12}
      labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
      legends={[
        {
          dataFrom: 'keys',
          anchor: 'bottom-right',
          direction: 'column',
          justify: false,
          translateX: 120,
          translateY: 0,
          itemsSpacing: 2,
          itemWidth: 100,
          itemHeight: 20,
          itemDirection: 'left-to-right',
          itemOpacity: 0.85,
          symbolSize: 20,
          effects: [
            {
              on: 'hover',
              style: {
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
    />
  );
};