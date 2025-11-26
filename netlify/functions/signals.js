const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();
        const params = event.queryStringParameters || {};
        const limit = Number(params.limit || 50);
        const symbol = params.symbol;

        let rows;
        if (symbol) {
            rows = await sql`
                SELECT * FROM signals 
                WHERE symbol = ${symbol} 
                ORDER BY signal_date DESC 
                LIMIT ${limit}
            `;
        } else {
            rows = await sql`
                SELECT * FROM signals 
                ORDER BY signal_date DESC 
                LIMIT ${limit}
            `;
        }

        return jsonResponse(200, { success: true, data: rows });
    } catch (error) {
        console.error('signals error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
