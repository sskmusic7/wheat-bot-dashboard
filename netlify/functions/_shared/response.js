function jsonResponse(statusCode, payload) {
    return {
        statusCode,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        body: JSON.stringify(payload)
    };
}

function handleOptions() {
    return jsonResponse(200, { success: true });
}

module.exports = {
    jsonResponse,
    handleOptions
};
