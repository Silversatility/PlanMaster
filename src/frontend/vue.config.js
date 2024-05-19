module.exports = {
  publicPath: "/dist/",
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].hash = true;
      return args;
    });
    config.plugins.delete('preload');
  },
  pwa: {
    workboxPluginMode: "InjectManifest",
    workboxOptions: {
      swSrc: "src/service-worker.js"
    },
    themeColor: "#b1e8dd",
    exclude: [/OneSignal.*\.js$/]
  }
};
