const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const { note_id } = body;

        if (!note_id) {
            return jsonResponse(400, { success: false, error: 'note_id required' });
        }

        const sql = requireSql();
        await sql`DELETE FROM notes WHERE id = ${note_id}`;
        return jsonResponse(200, { success: true, message: 'Note deleted successfully' });
    } catch (error) {
        console.error('delete_note error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
