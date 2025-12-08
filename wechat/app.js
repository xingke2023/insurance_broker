// app.js
App({
  globalData: {
    apiUrl: 'https://hongkong.xingke888.com'
  },

  onLaunch() {
    console.log('小程序启动，API地址:', this.globalData.apiUrl)
  }
})
