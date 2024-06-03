import { ResponsiveLine } from "@nivo/line";
import { LineData, colourScheme } from "@/utils/chartUtils";


interface LineChartProps {
  data: LineData;
  target: string;
  driftData?: any;
}

// have to ensure a max height is set on the parent: https://nivo.rocks/line/
export const LineChart = ({ data, target, driftData }: LineChartProps) =>  (
  <ResponsiveLine
    data={data}
    margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
    xScale={{
      type: "time",
      format: "%Y-%m-%d",
    }}
    yScale={{
      type: "linear",
      min: "auto",
      max: "auto",
      stacked: false,
      reverse: false,
    }}
    yFormat=" >-.2f"
    curve="cardinal"
    axisTop={null}
    axisRight={null}
    enableSlices="x"
    axisBottom={{
      tickSize: 5,
      tickPadding: 10,
      tickRotation: 30,
      legend: "Month",
      legendOffset: -10,
      legendPosition: "middle",
      truncateTickAt: 0,
      tickValues: "every month",
      format: "%Y-%m-%d",
    }}
    axisLeft={{
      tickSize: 8,
      tickPadding: 5,
      tickRotation: 0,
      legend: target,
      legendOffset: -50,
      legendPosition: "middle",
      truncateTickAt: 0,
      format: (value) => {
        if (value >= 10000) {
          return `${value / 1000}K`;
        }
        return `${value}`;
      },
    }}
    enableGridX={true}
    enableGridY={false}
    colors={({ id }) => colourScheme[id]}
    lineWidth={1}
    enablePoints={false}
    pointSize={2.5}
    pointColor={{ theme: "background" }}
    pointBorderWidth={2}
    pointBorderColor={{ from: "serieColor" }}
    //pointLabelYOffset={-12}
    areaOpacity={0.05}
    enableTouchCrosshair={true}
    //useMesh={true}

    areaBaselineValue={0} // Set the baseline value for the area
    legends={[
      {
        anchor: "right",
        direction: "column",
        justify: false,
        translateX: 100,
        translateY: 0,
        itemsSpacing: 0,
        itemDirection: "left-to-right",
        itemWidth: 80,
        itemHeight: 20,
        itemOpacity: 0.75,
        symbolSize: 12,
        symbolShape: "circle",
        symbolBorderColor: "rgba(0, 0, 0, .5)",
        data: [
          ...data.map((item) => ({
            id: item.id,
            label: item.id,
            color: colourScheme[item.id],
          })),
          ...(driftData &&
          Object.values(driftData).some(
            (drift: any) => drift.status === "Significant"
          )
            ? [
                {
                  id: "significant-drift",
                  label: "Drift",
                  color: "#b0413e",
                },
              ]
            : []),
        ],
      },
    ]}
    // sliceTooltip={CustomTooltip}
    // tooltip={DriftTooltip}
    markers={
      driftData &&
      Object.entries(driftData)
        .filter(([, drift]: [string, any]) => drift.status === "Significant")
        .map(([date, drift]: [string, any], index: number) => ({
          axis: "x",
          value: new Date(date.split("T")[0]), // Keep the date as the value
          lineStyle: { stroke: "#b0413e", strokeWidth: 1 },
          legend: `${index + 1}`, // Display the index as the legend
          legendOrientation: "horizontal",
          legendPosition: "top",
          textStyle: {
            fill: "#b0413e",
            fontWeight: "500",
            fontSize: "13px",
            backgroundColor: "#b0413e",
          },
        }))
    }
    //motionConfig="stiff"
  />
);