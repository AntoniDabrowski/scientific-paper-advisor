const path = require('path');

module.exports = {
    mode: 'production',
    entry: path.resolve(__dirname, 'scripts/content.js'), //'.scripts/content.js',
    output: {
        filename: 'content.js',
        path: path.resolve(__dirname, 'dist'),
    },
};