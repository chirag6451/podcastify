const webpack = require('webpack');

module.exports = {
  webpack: {
    configure: {
      resolve: {
        fallback: {
          "buffer": require.resolve("buffer/"),
          "stream": require.resolve("stream-browserify"),
          "url": require.resolve("url/"),
          "querystring": require.resolve("querystring-es3"),
          "https": require.resolve("https-browserify"),
          "http": require.resolve("stream-http"),
          "assert": require.resolve("assert/"),
          "os": require.resolve("os-browserify/browser"),
          "net": false,
          "tls": false,
          "fs": false
        }
      },
      plugins: [
        new webpack.ProvidePlugin({
          Buffer: ['buffer', 'Buffer'],
          process: 'process/browser',
        }),
      ]
    }
  }
};
