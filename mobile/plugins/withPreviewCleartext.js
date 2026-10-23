const { AndroidConfig, withAndroidManifest } = require('expo/config-plugins');

module.exports = (config, { enabled = false } = {}) =>
  withAndroidManifest(config, (mod) => {
    const application = AndroidConfig.Manifest.getMainApplicationOrThrow(mod.modResults);
    application.$['android:usesCleartextTraffic'] = enabled === true ? 'true' : 'false';
    return mod;
  });
