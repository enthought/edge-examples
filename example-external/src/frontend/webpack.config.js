module.exports = [
    // Entry for the login page
    {
        entry: './src/login.js',
        output: {
            path: __dirname + '/dist/',
            filename: 'login.js',
            publicPath: './dist/'
        },
        module: {
            rules: [
                {
                    test: /\.(js|jsx)$/,
                    exclude: /node_modules/,
                    use: ['babel-loader'],
                },
                { test: /\.css$/, use: ['style-loader', 'css-loader'] },
                {
                    // In .css files, svg is loaded as a data URI.
                    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                    issuer: /\.css$/,
                    use: {
                      loader: 'svg-url-loader',
                      options: { encoding: 'none', limit: 10000 }
                    }
                },
                {
                    // In .ts and .tsx files (both of which compile to .js), svg files
                    // must be loaded as a raw string instead of data URIs.
                    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                    issuer: /\.js$/,
                    use: {
                        loader: 'raw-loader'
                    }
                },
                {
                    test: /\.(png|jpg|gif|ttf|woff|woff2|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                    use: [{ loader: 'url-loader', options: { limit: 10000 } }]
                }
            ]
        },
        resolve: {
            extensions: ['*', '.js', '.jsx', '.css'],
        },
    },
    // Entry for the actual app
    {
        entry: './src/index.js',
        output: {
            path: __dirname + '/dist/',
            filename: 'index.js',
            publicPath: './dist/'
        },
        module: {
            rules: [
                {
                    test: /\.(js|jsx)$/,
                    exclude: /node_modules/,
                    use: ['babel-loader'],
                },
                { test: /\.css$/, use: ['style-loader', 'css-loader'] },
                {
                    // In .css files, svg is loaded as a data URI.
                    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                    issuer: /\.css$/,
                    use: {
                      loader: 'svg-url-loader',
                      options: { encoding: 'none', limit: 10000 }
                    }
                },
                {
                    // In .ts and .tsx files (both of which compile to .js), svg files
                    // must be loaded as a raw string instead of data URIs.
                    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                    issuer: /\.js$/,
                    use: {
                        loader: 'raw-loader'
                    }
                },
                {
                    test: /\.(png|jpg|gif|ttf|woff|woff2|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                    use: [{ loader: 'url-loader', options: { limit: 10000 } }]
                }
            ]
        },
        resolve: {
            extensions: ['*', '.js', '.jsx', '.css'],
        },
    },
];
