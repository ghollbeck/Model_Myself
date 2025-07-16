import React from 'react';

interface ResponseDisplayProps {
    response: string;
    error: string;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ response, error }) => (
    <>
        {response && (
            <div className="response">
                <h3>Response:</h3>
                <p>{response}</p>
            </div>
        )}
        {error && (
            <div className="response error">
                <h3>Error:</h3>
                <p>{error}</p>
            </div>
        )}
    </>
);

export default ResponseDisplay; 