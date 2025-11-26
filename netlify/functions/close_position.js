const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const { position_id, exit_price, exit_reason = 'manual', notes = null } = body;

        if (!position_id || !exit_price) {
            return jsonResponse(400, { success: false, error: 'position_id and exit_price required' });
        }

        const sql = requireSql();
        const positions = await sql`SELECT * FROM positions WHERE id = ${position_id}`;
        if (!positions.length) {
            return jsonResponse(404, { success: false, error: 'Position not found' });
        }

        const position = positions[0];
        if (!position.is_open) {
            return jsonResponse(400, { success: false, error: 'Position already closed' });
        }

        const pnl = (Number(exit_price) - Number(position.entry_price)) * Number(position.quantity);
        const pnlPct = ((Number(exit_price) - Number(position.entry_price)) / Number(position.entry_price)) * 100;
        const proceeds = Number(position.quantity) * Number(exit_price);

        await sql`UPDATE positions SET is_open = FALSE, updated_at = NOW() WHERE id = ${position_id}`;

        await sql`
            INSERT INTO trades (symbol, quantity, entry_price, exit_price, entry_date, exit_date, pnl, pnl_pct, source, exit_reason, notes)
            VALUES (
                ${position.symbol}, ${position.quantity}, ${position.entry_price}, ${exit_price},
                ${position.entry_date}, NOW(), ${pnl}, ${pnlPct}, ${position.source}, ${exit_reason}, ${notes}
            )
        `;

        const perfRows = await sql`SELECT cash_balance FROM performance ORDER BY date DESC LIMIT 1`;
        const currentCash = perfRows.length ? Number(perfRows[0].cash_balance) : 0;
        const newCash = currentCash + proceeds;

        const openPositions = await sql`SELECT quantity, entry_price FROM positions WHERE is_open = TRUE`;
        const totalPositionValue = openPositions.reduce((sum, pos) => sum + Number(pos.quantity) * Number(pos.entry_price), 0);
        const newPortfolio = newCash + totalPositionValue;

        const totalPnlRows = await sql`SELECT COALESCE(SUM(pnl), 0) AS total_pnl FROM trades`;
        const totalPnl = Number(totalPnlRows[0].total_pnl || 0);
        const currentDate = new Date().toISOString().slice(0, 10);

        await sql`DELETE FROM performance WHERE date = ${currentDate}`;
        await sql`
            INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
            VALUES (${currentDate}, ${position.source}, ${newCash}, ${newPortfolio}, ${totalPnl}, 0)
        `;

        return jsonResponse(200, {
            success: true,
            pnl,
            pnl_pct: pnlPct,
            proceeds,
            new_cash_balance: newCash,
            message: `Position closed. P&L: $${pnl.toFixed(2)} (${pnlPct.toFixed(2)}%)`
        });
    } catch (error) {
        console.error('close_position error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
