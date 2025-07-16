import React from 'react';

interface LogsProps {
    logs: string[];
}

const Logs: React.FC<LogsProps> = ({ logs }) => (
    <div className="logs">
        <h3>Console Logs:</h3>
        {logs.map((log, index) => (
            <div key={index}>{log}</div>
        ))}
    </div>
);

export default Logs; 