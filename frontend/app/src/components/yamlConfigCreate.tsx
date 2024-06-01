import { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";

import { Input } from "./ui/input";
import { Label } from "./ui/label";


import { Checkbox } from "./ui/checkbox";
import { CheckedState } from "@radix-ui/react-checkbox";

import { DatePicker } from "./ui/date-picker";

interface YamlConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfigCreate: (file: File) => void;
}

export const YamlConfigDialog: React.FC<YamlConfigDialogProps> = ({
  open,
  onOpenChange,
  onConfigCreate,
}) => {
  const [freq, setFreq] = useState("W");
  const [dateColumn, setDateColumn] = useState("DATE");
  const [inputChunkLength, setInputChunkLength] = useState(12);
  const [forecastLength, setForecastLength] = useState(12);
  const [targets, setTargets] = useState({
    jumbo: "DRIVINGADVANCE",
    bogging: "PRIMARY_TONNES",
    lhdrilling: "LONGHOLEMETRES",
    trucking: "TKM",
    trucking_surface_ore: "ORE_TONNES_TO_SURFACE",
  });
  const [newDatesPrediction, setNewDatesPrediction] = useState(true);
  const [numTestPrediction, setNumTestPrediction] = useState(5);
  const [startDate, setStartDate] = useState<Date | undefined>(
    new Date("2021-01-01")
  );

  const handleNewDatesPredictionChange = (checked: CheckedState) => {
    setNewDatesPrediction(checked === true);
  };

  const handleCreate = () => {
    const yamlContent = `
freq: "${freq}"
date_column: "${dateColumn}"
input_chunk_length: ${inputChunkLength}
forecast_length: ${forecastLength}

targets:
  jumbo: "${targets.jumbo}"
  bogging: "${targets.bogging}"
  lhdrilling: "${targets.lhdrilling}"
  trucking: "${targets.trucking}"
  trucking_surface_ore: "${targets.trucking_surface_ore}"

new_dates_prediction: ${newDatesPrediction}
num_test_prediction: ${numTestPrediction}
start_date: "${startDate}"
    `;

    const yamlFile = new File([yamlContent], "config.yaml", {
      type: "text/yaml",
    });

    onConfigCreate(yamlFile);
    onOpenChange(false);
  };

  return (
    <div className="text-slate-900">
      <AlertDialog open={open} onOpenChange={onOpenChange}>
      <div className="w-[600px]">
        <AlertDialogContent className="w-12/12 ">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-slate-900">
              Create Configuration File
            </AlertDialogTitle>
            <AlertDialogDescription className="text-slate-900">
              Fill in the following fields to create a YAML configuration file:
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="grid gap-4 py-4 text-slate-900">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="freq">Frequency:</Label>
              <Input
                id="freq"
                value={freq}
                onChange={(e) => setFreq(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="date_column">Date Column:</Label>
              <Input
                id="date_column"
                value={dateColumn}
                onChange={(e) => setDateColumn(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="input_chunk_length">Input Chunk Length:</Label>
              <Input
                id="input_chunk_length"
                type="number"
                value={inputChunkLength}
                onChange={(e) => setInputChunkLength(Number(e.target.value))}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="forecast_length">Forecast Length:</Label>
              <Input
                id="forecast_length"
                type="number"
                value={forecastLength}
                onChange={(e) => setForecastLength(Number(e.target.value))}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="targets">Targets:</Label>
              <div className="col-span-3 grid gap-2">
                <div className="flex items-center gap-4">
                  <Label htmlFor="jumbo">jumbo:</Label>
                  <Input
                    id="jumbo"
                    value={targets.jumbo}
                    onChange={(e) =>
                      setTargets({ ...targets, jumbo: e.target.value })
                    }
                  />
                </div>
                <div className="flex items-center gap-4">
                  <Label htmlFor="bogging">bogging:</Label>
                  <Input
                    id="bogging"
                    value={targets.bogging}
                    onChange={(e) =>
                      setTargets({ ...targets, bogging: e.target.value })
                    }
                  />
                </div>
                <div className="flex items-center gap-4">
                  <Label htmlFor="lhdrilling">lhdrilling:</Label>
                  <Input
                    id="lhdrilling"
                    value={targets.lhdrilling}
                    onChange={(e) =>
                      setTargets({ ...targets, lhdrilling: e.target.value })
                    }
                  />
                </div>
                <div className="flex items-center gap-4">
                  <Label htmlFor="trucking">trucking:</Label>
                  <Input
                    id="trucking"
                    value={targets.trucking}
                    onChange={(e) =>
                      setTargets({ ...targets, trucking: e.target.value })
                    }
                  />
                </div>
                <div className="flex items-center gap-4">
                  <Label htmlFor="trucking_surface_ore">
                    trucking_surface_ore:
                  </Label>
                  <Input
                    id="trucking_surface_ore"
                    value={targets.trucking_surface_ore}
                    onChange={(e) =>
                      setTargets({
                        ...targets,
                        trucking_surface_ore: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="new_dates_prediction">New Dates Prediction:</Label>
                <Checkbox
                id="new_dates_prediction"
                checked={newDatesPrediction}
                onCheckedChange={handleNewDatesPredictionChange}
                />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="num_test_prediction">
                Backtesting Period Count:
              </Label>
              <Input
                id="num_test_prediction"
                type="number"
                value={numTestPrediction}
                onChange={(e) => setNumTestPrediction(Number(e.target.value))}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="start_date">Start Date:</Label>
            <DatePicker
            selected={startDate}
            onSelect={(date) => setStartDate(date)}
            />
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel className="text-slate-900">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              className="text-slate-50"
              onClick={handleCreate}
            >
              Create
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
        </div>
      </AlertDialog>
    </div>
  );
};
