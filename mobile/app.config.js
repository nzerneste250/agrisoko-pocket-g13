module.exports = ({ config }) => {
  const apiUrl = (process.env.EXPO_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
  const allowPreviewHttp =
    process.env.EAS_BUILD_PROFILE === 'preview' &&
    apiUrl === 'http://172.30.114.74:8000';

  return {
    ...config,
    plugins: [
      ...(config.plugins ?? []),
      ['./plugins/withPreviewCleartext', { enabled: allowPreviewHttp }],
    ],
  };
};
