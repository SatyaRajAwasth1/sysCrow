import { ModelInfoCard, ModelHyperparameters } from "@/components/ui/model_info";
import { Card, CardContent } from "@/components/ui/card"
import { ResponsiveContainer, YAxis, Tooltip, LineChart, Line, XAxis } from "recharts";

const model1Metrics = [
  { name: 'Accuracy', value:0 },
  { name: 'Precision', value:0 },
  { name: 'Recall', value:0 },
  { name: 'F1 Score', value:0 }
];

const model1PerformanceHistory = [
  { date: '2025-01-01', accuracy: 0, latency: 0 },
  { date: '2025-01-02', accuracy: 0, latency: 0 },
  { date: '2025-01-03', accuracy: 0, latency: 0 },
  // More data points...
];

async function fetchData() {
  const apiUrl = 'localhost://model1/info'; // Replace with your API URL
  try {
      // Make an HTTP GET request to fetch the JSON data
      const response = await fetch(apiUrl);
      
      if (response.ok) {
          const data = await response.json();  // Parse the JSON data
          return data;
      }
    }
    catch(error){
      console.log("error fetching model information:", error)
    }
  }

export default function Model1() {
  const model1Info = {
    "Type": "Voting Experts Model",
    "Framework": "PyTorch",
    "Last Updated": "2025-02-18",
    "Version": "-"
  };
  
  const model1Hyperparameters = {
    "window_size": "7",
    "voting_expert_threshold": "4",
    "suspiciousness_score_threshold": "0.5",
    // "optimizer": "Adam",
    // "dropout": "0.25",
    // "activation": "ReLU",
    // "layers": "4",
    // "hidden_units": "128,256,128,64",
    // "regularization": "L2 (0.001)"
  };
  
  return (
    <div className="space-y-6">
      <ModelInfoCard 
        title="Unsupervised Context Based Fault Localization Model" 
        description="unsupervised sequence segmentation model for context-based fault localization."
        metadata={model1Info}
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Card className="bg-gray-900">
          <CardContent className="p-4">
            <h2 className="text-xl font-semibold mb-3">Current Model Metrics</h2>
            <div className="space-y-4">
              {model1Metrics.map((metric) => (
                <div key={metric.name} className="relative pt-1">
                  <div className="flex justify-between items-center mb-1">
                    <div className="text-gray-300">{metric.name}</div>
                    <div className="text-blue-300">{metric.value.toFixed(2)}</div>
                  </div>
                  <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-700">
                    <div 
                      style={{ width: `${metric.value * 100}%` }}
                      className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gray-900">
          <CardContent className="p-4">
            <h2 className="text-xl font-semibold mb-3">Performance History</h2>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={model1PerformanceHistory}>
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis yAxisId="left" stroke="#3B82F6" />
                <YAxis yAxisId="right" orientation="right" stroke="#EF4444" />
                <Tooltip />
                <Line yAxisId="left" type="monotone" dataKey="accuracy" stroke="#3B82F6" />
                <Line yAxisId="right" type="monotone" dataKey="latency" stroke="#EF4444" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      <ModelHyperparameters parameters={model1Hyperparameters} />
    </div>
  );
}