import { Card, CardContent } from "@/components/ui/card";

function ModelInfoCard({ title, description, metadata }) {
    return (
      <Card className="bg-gray-900 mb-6">
        <CardContent className="p-4">
          <h2 className="text-xl font-semibold mb-2">{title}</h2>
          <p className="text-gray-300 mb-4">{description}</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key} className="bg-gray-800 p-3 rounded-lg">
                <div className="text-gray-400 text-xs mb-1">{key}</div>
                <div className="text-white font-medium">{value}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }
  
  function ModelHyperparameters({ parameters }) {
    return (
      <Card className="bg-gray-900 mb-6">
        <CardContent className="p-4">
          <h2 className="text-xl font-semibold mb-3">Model Hyperparameters</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(parameters).map(([key, value]) => (
              <div key={key} className="flex justify-between p-2 bg-gray-800/50 rounded-lg">
                <span className="text-gray-300">{key}:</span>
                <span className="text-blue-300 font-mono">{value}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  export { ModelInfoCard, ModelHyperparameters }