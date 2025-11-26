const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    // Placeholder: actual polling runs locally; this just acknowledges the request
    return jsonResponse(200, {
        success: true,
        message: 'News polling runs on your local bot. Dashboard refresh triggered successfully.'
    });
};
