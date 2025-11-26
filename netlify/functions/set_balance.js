const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');
const { parseBody } = require('./_shared/utils');

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const body = parseBody(event);
        const { balance } = body;

        if (balance === undefined) {
            return jsonResponse(400, { success: false, error: 'balance required' });
        }

        const sql = requireSql();
        const openPositions = await sql`SELECT quantity, entry_price FROM positions WHERE is_open = TRUE`;
        const positionValue = openPositions.reduce((sum, pos) => sum + Number(pos.quantity) * Number(pos.entry_price), 0);
        const portfolioValue = Number(balance) + positionValue;
        const currentDate = new Date().toISOString().slice(0, 10);

        await sql`
            INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
            VALUES (${currentDate}, 'manual', ${balance}, ${portfolioValue}, 0, 0)
            ON CONFLICT (date) DO UPDATE SET
                cash_balance = excluded.cash_balance,
                portfolio_value = excluded.portfolio_value,
                total_pnl = excluded.total_pnl,
                daily_return = excluded.daily_return,
                source = excluded.source
        `;

        return jsonResponse(200, {
            success: true,
            balance: Number(balance),
            portfolio_value: portfolioValue
        });
    } catch (error) {
        console.error('set_balance error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
