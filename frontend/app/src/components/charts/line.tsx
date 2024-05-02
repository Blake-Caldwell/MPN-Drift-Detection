import { ResponsiveLineCanvas} from '@nivo/line'
import { LineData } from '@/utils/chartUtils'

import { useState } from 'react';


type LineChartProps = {
    data: LineData;
  };

  
  
// have to ensure a max height is set on the parent: https://nivo.rocks/line/
export const LineChart = ({data} : LineChartProps) => (

    <ResponsiveLineCanvas
    data={data}
    margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
    xScale={{
        type: "time",
        format: "%Y-%m-%d"
      }}
    yScale={{
        type: 'linear',
        min: 'auto',
        max: 'auto',
        stacked: false,
        reverse: false
    }}
    yFormat=" >-.2f"
    curve="cardinal"
    axisTop={null}
    axisRight={null}
    
    axisBottom={{
        tickSize: 5,
        tickPadding: 10,
        tickRotation: 30,
        legend: 'Month',
        legendOffset: -10,
        legendPosition: 'middle',
        truncateTickAt: 0,
        tickValues: 'every month',
        format: "%Y-%m-%d"
    }}
    axisLeft={{
        tickSize: 8,
        tickPadding: 5,
        tickRotation: 0,
        legend: 'Count',
        legendOffset: -50,
        legendPosition: 'middle',
        truncateTickAt: 0,
        format: (value) => {
            return `${value / 1000}K`
        }
    }}
    enableGridX={true}
    enableGridY={false}
    colors={{ scheme: 'category10' }}
    lineWidth={1}
    enablePoints={true}
    pointSize={2.5}
    pointColor={{ theme: 'background' }}
    pointBorderWidth={2}
    pointBorderColor={{ from: 'serieColor' }}
    //pointLabelYOffset={-12}
    areaOpacity={0.05}
    enableTouchCrosshair={true}
    //useMesh={true}

    areaBaselineValue={0} // Set the baseline value for the area
    
    legends={[
        {
            anchor: 'right',
            direction: 'column',
            justify: false,
            translateX: 100,
            translateY: 0,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 80,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
            effects: [
                {
                    on: 'hover',
                    style: {
                        itemBackground: 'rgba(0, 0, 0, .03)',
                        itemOpacity: 1
                    }
                }
            ]
        }
    ]}
    //motionConfig="stiff"
/>

)