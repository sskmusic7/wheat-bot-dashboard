function parseBody(event) {
    if (!event.body) return {};
    try {
        return JSON.parse(event.body);
    } catch (err) {
        throw new Error('Invalid JSON body');
    }
}

module.exports = {
    parseBody
};
