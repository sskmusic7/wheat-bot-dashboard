const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();
        const params = event.queryStringParameters || {};
        const limit = Number(params.limit || 50);
        const unreadOnly = params.unread_only === 'true';

        const rows = await sql`
            SELECT * FROM news_alerts
            WHERE 1=1
            ${unreadOnly ? sql`AND is_read = FALSE` : sql``}
            ORDER BY received_at DESC
            LIMIT ${limit}
        `;

        const unread = await sql`SELECT COUNT(*) AS count FROM news_alerts WHERE is_read = FALSE`;

        return jsonResponse(200, {
            success: true,
            data: rows,
            unread_count: Number(unread[0].count || 0)
        });
    } catch (error) {
        console.error('news_alerts error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
