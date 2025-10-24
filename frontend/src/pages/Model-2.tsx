import { ModelInfoCard, ModelHyperparameters } from "@/components/ui/model_info";
import { Card, CardContent } from "@/components/ui/card"
import { ResponsiveContainer, YAxis, Tooltip, LineChart, Line, XAxis } from "recharts";
import ModelStream from "../services/ModelStream";

const model1Metrics = [
  { name: 'Accuracy', value: 0 },
  { name: 'Precision', value: 0.92794 },
  { name: 'Recall', value: 0.92226 },
  { name: 'F1 Score', value: 0.92509 }
];

const model1PerformanceHistory = [
  { date: '2025-01-01', accuracy: 0, latency: 0 },
  { date: '2025-01-02', accuracy: 0, latency: 0 },
  { date: '2025-01-03', accuracy: 0, latency: 0 },
  // More data points...
];


export default function Model1() {
  const model1Info = {
    "Type": "Deep Neural Network",
    "Framework": "PyTorch",
    "Last Updated": "NA",
    "Version": "NA"
  };
  
  const model1Hyperparameters = {
    "number of classes": 28,
    "batch size": "2048",
    "epochs": "300",
    "optimizer": "Adam",
    "layers": "4",
    "hidden size": "64",
    "regularization": "L2 (0.001)",
    "input size":1,
    "number of layers": 2,
    "number of candidates": 9
  };
  
  return (
    <div className="space-y-6">
      <ModelInfoCard 
        title="Anomaly Detection Model" 
        description="Deep learning model for detecting anomalies in system logs and metrics data."
        metadata={model1Info}
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

        <Card className="bg-gray-900 col-span-3">
                  <CardContent className="p-4">
                    <h2 className="text-xl font-semibold mb-3">Model Evaluation Log Stream</h2>
                    <ModelStream />
                  </CardContent>
                </Card>

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