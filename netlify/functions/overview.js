const { requireSql } = require('./_shared/db');
const { jsonResponse, handleOptions } = require('./_shared/response');

const formatStats = (row) => {
    if (!row) {
        return {
            total_trades: 0,
            total_pnl: 0,
            avg_pnl_pct: 0,
            winning_trades: 0,
            losing_trades: 0
        };
    }

    return {
        total_trades: Number(row.total_trades || 0),
        total_pnl: Number(row.total_pnl || 0),
        avg_pnl_pct: Number(row.avg_pnl_pct || 0),
        winning_trades: Number(row.winning_trades || 0),
        losing_trades: Number(row.losing_trades || 0)
    };
};

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const sql = requireSql();

        const positions = await sql`
            SELECT * FROM positions
            WHERE is_open = TRUE
            ORDER BY entry_date DESC
        `;

        const perfRows = await sql`
            SELECT * FROM performance
            ORDER BY date DESC
            LIMIT 1
        `;

        const stats30 = await sql`
            SELECT 
                COUNT(*) AS total_trades,
                COALESCE(SUM(pnl), 0) AS total_pnl,
                COALESCE(AVG(pnl_pct), 0) AS avg_pnl_pct,
                COALESCE(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END), 0) AS winning_trades,
                COALESCE(SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END), 0) AS losing_trades
            FROM trades
            WHERE exit_date >= NOW() - INTERVAL '30 days'
        `;

        const stats7 = await sql`
            SELECT 
                COUNT(*) AS total_trades,
                COALESCE(SUM(pnl), 0) AS total_pnl,
                COALESCE(AVG(pnl_pct), 0) AS avg_pnl_pct,
                COALESCE(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END), 0) AS winning_trades,
                COALESCE(SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END), 0) AS losing_trades
            FROM trades
            WHERE exit_date >= NOW() - INTERVAL '7 days'
        `;

        const positionValue = positions.reduce((sum, pos) => sum + Number(pos.quantity) * Number(pos.entry_price), 0);

        return jsonResponse(200, {
            success: true,
            data: {
                portfolio_value: perfRows.length ? Number(perfRows[0].portfolio_value) : positionValue,
                cash_balance: perfRows.length ? Number(perfRows[0].cash_balance) : 0,
                position_value: positionValue,
                total_positions: positions.length,
                stats_30d: formatStats(stats30[0]),
                stats_7d: formatStats(stats7[0])
            }
        });
    } catch (error) {
        console.error('overview error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
