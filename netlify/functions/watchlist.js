const { jsonResponse, handleOptions } = require('./_shared/response');

const defaultSymbols = ['WEAT', 'SOYB', 'CORN', 'DBA', 'ADM', 'BG'];

async function fetchQuote(symbol) {
    try {
        const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`);
        const data = await res.json();
        const meta = data?.chart?.result?.[0]?.meta;
        if (!meta) return null;
        return {
            symbol,
            price: meta.regularMarketPrice,
            change: meta.regularMarketChange,
            changePercent: meta.regularMarketChangePercent,
            volume: meta.regularMarketVolume
        };
    } catch (error) {
        console.error('fetchQuote error', symbol, error.message);
        return null;
    }
}

exports.handler = async (event) => {
    if (event.httpMethod === 'OPTIONS') return handleOptions();

    try {
        const params = event.queryStringParameters || {};
        const symbols = params.symbols ? params.symbols.split(',') : defaultSymbols;
        const quotes = await Promise.all(symbols.map(fetchQuote));
        return jsonResponse(200, { success: true, data: quotes.filter(Boolean) });
    } catch (error) {
        console.error('watchlist error', error);
        return jsonResponse(500, { success: false, error: error.message });
    }
};
