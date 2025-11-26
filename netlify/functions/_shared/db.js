const { neon } = require('@netlify/neon');

const connectionString = process.env.NETLIFY_DATABASE_URL || process.env.NEON_DATABASE_URL;

if (!connectionString) {
    console.warn('NETLIFY_DATABASE_URL not configured. Netlify functions will fail until set.');
}

let sqlInstance = null;
if (connectionString) {
    sqlInstance = neon(connectionString);
}

function requireSql() {
    if (!sqlInstance) {
        throw new Error('Database connection not initialized.');
    }
    return sqlInstance;
}

module.exports = {
    sql: sqlInstance,
    requireSql
};
