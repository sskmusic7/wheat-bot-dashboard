const { jsonResponse, handleOptions } = require('./_shared/response');

async function fetchQuote(symbol) {
    const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`);
    if (!res.ok) throw new Error('Symbol not found');
    const data = await res.json();
    const meta = data?.chart?.result?.[0]?.meta;
    if (!meta) throw new Error('Symbol not found');
    return {
        symbol,
        price: meta.regularMarketPrice,
        change: meta.regularMarketChange,
        changePercent: meta.regularMarketChangePercent,
        volume: meta.regularMarketVolume,
        currency: meta.currency || 'USD'
    };
}

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const match = event.path.match(/quote\/(.+)$/);
        const symbol = match ? match[1] : null;
        if (!symbol) {
            return jsonResponse(400, { success: false, error: 'symbol required' });
        }

        const quote = await fetchQuote(symbol);
        return jsonResponse(200, { success: true, data: quote });
    } catch (error) {
        console.error('quote error', error);
        return jsonResponse(404, { success: false, error: error.message });
    }
};
