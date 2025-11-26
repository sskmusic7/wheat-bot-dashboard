const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();
        const rows = await sql`
            SELECT * FROM strategy_stats
            ORDER BY total_pnl DESC
            LIMIT 10
        `;
        return jsonResponse(200, { success: true, data: rows });
    } catch (error) {
        console.error('strategies error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
