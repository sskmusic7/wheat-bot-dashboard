const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const { alert_id = null, mark_all = false } = body;
        const sql = requireSql();

        if (mark_all) {
            await sql`UPDATE news_alerts SET is_read = TRUE WHERE is_read = FALSE`;
        } else if (alert_id) {
            await sql`UPDATE news_alerts SET is_read = TRUE WHERE id = ${alert_id}`;
        } else {
            return jsonResponse(400, { success: false, error: 'alert_id or mark_all required' });
        }

        return jsonResponse(200, { success: true });
    } catch (error) {
        console.error('news_alerts_mark_read error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
