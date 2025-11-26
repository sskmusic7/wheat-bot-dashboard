const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();
        const params = event.queryStringParameters || {};
        const limit = Number(params.limit || 100);
        const symbol = params.symbol;
        const source = params.source;

        let rows;
        if (symbol && source) {
            rows = await sql`
                SELECT * FROM trades 
                WHERE symbol = ${symbol} AND source = ${source} 
                ORDER BY exit_date DESC 
                LIMIT ${limit}
            `;
        } else if (symbol) {
            rows = await sql`
                SELECT * FROM trades 
                WHERE symbol = ${symbol} 
                ORDER BY exit_date DESC 
                LIMIT ${limit}
            `;
        } else if (source) {
            rows = await sql`
                SELECT * FROM trades 
                WHERE source = ${source} 
                ORDER BY exit_date DESC 
                LIMIT ${limit}
            `;
        } else {
            rows = await sql`
                SELECT * FROM trades 
                ORDER BY exit_date DESC 
                LIMIT ${limit}
            `;
        }

        return jsonResponse(200, { success: true, data: rows });
    } catch (error) {
        console.error('trades error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
