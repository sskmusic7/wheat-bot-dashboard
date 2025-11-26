const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();
        const params = event.queryStringParameters || {};
        const category = params.category;

        let rows;
        if (category) {
            rows = await sql`
                SELECT * FROM notes 
                WHERE category = ${category} 
                ORDER BY created_at DESC 
                LIMIT 100
            `;
        } else {
            rows = await sql`
                SELECT * FROM notes 
                ORDER BY created_at DESC 
                LIMIT 100
            `;
        }

        return jsonResponse(200, { success: true, data: rows });
    } catch (error) {
        console.error('notes error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
