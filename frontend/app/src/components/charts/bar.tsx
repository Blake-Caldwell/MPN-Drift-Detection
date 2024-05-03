import { ResponsiveBar } from '@nivo/bar';
import { BarData } from '@/utils/chartUtils';

type BarChartProps = {
  data: BarData;
};

export const BarChart = ({ data }: BarChartProps) => {
  const keys = ["Actual", "LSTM", 
  "LSTM_low", "LSTM_high"
];

  console.log(data)

  return (
    <ResponsiveBar
      data={data}
      keys={keys}
      indexBy="date"
      margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
      padding={0.3}
      innerPadding={2.5}
      groupMode="grouped"
      valueScale={{ type: 'linear' }}
      indexScale={{ type: 'band', round: true }}
      colors={{ scheme: 'category10' }}
      borderWidth={3}
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
        legend: 'Sum',
        legendPosition: 'middle',
        legendOffset: -50,
        format: (value) => {
            return `${value / 1000}K`
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