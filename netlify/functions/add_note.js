const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const { title, content, category = 'general', tags = null } = body;

        if (!title || !content) {
            return jsonResponse(400, { success: false, error: 'title and content required' });
        }

        const sql = requireSql();
        const inserted = await sql`
            INSERT INTO notes (title, content, category, tags)
            VALUES (${title}, ${content}, ${category}, ${tags})
            RETURNING id
        `;

        return jsonResponse(200, {
            success: true,
            note_id: inserted[0].id,
            message: 'Note added successfully'
        });
    } catch (error) {
        console.error('add_note error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
