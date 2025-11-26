const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const {
            symbol,
            quantity,
            entry_price,
            source = 'manual',
            stop_loss = null,
            take_profit = null,
            notes = null
        } = body;

        if (!symbol || !quantity || !entry_price) {
            return jsonResponse(400, { success: false, error: 'symbol, quantity, entry_price required' });
        }

        const sql = requireSql();
        const cost = Number(quantity) * Number(entry_price);
        const perfRows = await sql`
            SELECT cash_balance FROM performance
            ORDER BY date DESC
            LIMIT 1
        `;
        const currentCash = perfRows.length ? Number(perfRows[0].cash_balance) : 0;

        if (cost > currentCash) {
            return jsonResponse(400, {
                success: false,
                error: `Insufficient funds. Need $${cost.toFixed(2)}, have $${currentCash.toFixed(2)}`
            });
        }

        const inserted = await sql`
            INSERT INTO positions (symbol, quantity, entry_price, entry_date, source, stop_loss, take_profit, notes)
            VALUES (${symbol}, ${quantity}, ${entry_price}, NOW(), ${source}, ${stop_loss}, ${take_profit}, ${notes})
            RETURNING id
        `;

        const openPositions = await sql`
            SELECT quantity, entry_price FROM positions WHERE is_open = TRUE
        `;
        const totalPositionValue = openPositions.reduce((sum, pos) => sum + Number(pos.quantity) * Number(pos.entry_price), 0);
        const newCash = currentCash - cost;
        const newPortfolio = newCash + totalPositionValue;
        const currentDate = new Date().toISOString().slice(0, 10);

        await sql`DELETE FROM performance WHERE date = ${currentDate}`;
        await sql`
            INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
            VALUES (${currentDate}, ${source}, ${newCash}, ${newPortfolio}, 0, 0)
        `;

        return jsonResponse(200, {
            success: true,
            position_id: inserted[0].id,
            message: `Position ${symbol} added successfully`
        });
    } catch (error) {
        console.error('add_position error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
