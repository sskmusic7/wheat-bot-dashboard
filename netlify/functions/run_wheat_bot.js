const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    return jsonResponse(200, {
        success: true,
        message: 'Remote Wheat Bot trigger acknowledged. Run the bot locally to generate fresh signals.'
    });
};
