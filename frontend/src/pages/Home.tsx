import { useState, useEffect } from 'react';
import { ResponsiveContainer, BarChart, Bar, YAxis, Tooltip, XAxis, Legend } from 'recharts';
import { Card, CardContent } from '@/components/ui/card';

const categoryColors = {
    INFORMATIVE: "#3B82F6", // Blue
    WARNING: "#FACC15",     // Yellow
    ERROR: "#EF4444",       // Red
    CRITICAL: "#B91C1C",    // Dark Red
    DEBUG: "#10B981",       // Green
    UNKNOWN: "#6B7280"      // Gray
};

const timeBasedLogData = [
    { time: '00:00', INFORMATIVE: 15, WARNING: 8, ERROR: 3, CRITICAL: 1, DEBUG: 12, UNKNOWN: 2 },
    { time: '04:00', INFORMATIVE: 18, WARNING: 10, ERROR: 4, CRITICAL: 2, DEBUG: 14, UNKNOWN: 1 },
    { time: '08:00', INFORMATIVE: 25, WARNING: 15, ERROR: 6, CRITICAL: 3, DEBUG: 22, UNKNOWN: 2 },
    { time: '12:00', INFORMATIVE: 32, WARNING: 22, ERROR: 8, CRITICAL: 5, DEBUG: 24, UNKNOWN: 3 },
    { time: '16:00', INFORMATIVE: 20, WARNING: 18, ERROR: 7, CRITICAL: 3, DEBUG: 16, UNKNOWN: 1 },
    { time: '20:00', INFORMATIVE: 10, WARNING: 7, ERROR: 2, CRITICAL: 1, DEBUG: 7, UNKNOWN: 1 }
];

function TimeBasedLogHistogram() {
    const [timeBasedLevelWiseData, setTimeBasedLevelWiseData] = useState([]);

    useEffect(() => {
        // Fetch data from API
        fetch('http://localhost:8000/logs/level/counts', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            setTimeBasedLevelWiseData(data);  // Update state with fetched data
        })
        .catch(error => {
            console.error('Error:', error);
            setTimeBasedLevelWiseData(timeBasedLogData);  // Fallback data in case of error
        });
    }, []);  // Empty dependency array ensures this runs once when the component mounts

    const totalLogs = timeBasedLevelWiseData.reduce((sum, timePoint) => {
        const timeSum = Object.keys(timePoint)
            .filter(key => key !== 'time')
            .reduce((acc, category) => acc + timePoint[category], 0);
        return sum + timeSum;
    }, 0);

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="font-medium text-white">Log Distribution (24h)</h3>
                <span className="text-sm text-gray-400">{totalLogs} total logs</span>
            </div>

            {timeBasedLevelWiseData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart
                        data={timeBasedLevelWiseData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                        <XAxis dataKey="time" stroke="#6B7280" fontSize={12} />
                        <YAxis stroke="#6B7280" fontSize={12} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(17, 24, 39, 0.9)',
                                border: 'none',
                                borderRadius: '4px',
                                color: '#fff'
                            }}
                            formatter={(value, name) => [`${value} logs`, name]}
                        />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                            iconSize={8}
                            wrapperStyle={{ fontSize: '12px' }}
                        />
                        {Object.keys(categoryColors).map((category) => (
                            <Bar
                                key={category}
                                dataKey={category}
                                stackId="a"
                                fill={categoryColors[category]}
                            />
                        ))}
                    </BarChart>
                </ResponsiveContainer>
            ) : (
                <div className="text-gray-400">Loading logs...</div>
            )}
        </div>
    );
}

export default TimeBasedLogHistogram;
