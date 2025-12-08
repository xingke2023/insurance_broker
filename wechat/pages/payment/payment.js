const app = getApp()

Page({
  data: {
    selectedPlan: 'yearly', // 默认选择包年
    selectedPrice: 699, // 默认价格
    plans: [],
    paying: false,
    loading: true
  },

  onLoad(options) {
    // 从API获取会员套餐
    this.fetchMembershipPlans()

    // 可以从URL参数接收默认选择的套餐
    if (options.plan) {
      this.setData({
        selectedPlan: options.plan
      })
    }
  },

  // 从API获取会员套餐
  fetchMembershipPlans() {
    wx.request({
      url: app.globalData.apiUrl + '/api/payment/plans',
      method: 'GET',
      success: (res) => {
        console.log('获取会员套餐成功:', res.data)

        if (res.data.code === 200 && res.data.data) {
          const plans = res.data.data

          // 找到默认选中的套餐
          let defaultPlan = plans.find(p => p.popular) || plans[0]

          this.setData({
            plans: plans,
            selectedPlan: defaultPlan ? defaultPlan.id : '',
            selectedPrice: defaultPlan ? defaultPlan.price : 0,
            loading: false
          })
        } else {
          wx.showToast({
            title: '获取套餐失败',
            icon: 'none'
          })
          this.setData({ loading: false })
        }
      },
      fail: (err) => {
        console.error('获取会员套餐失败:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  // 选择套餐
  selectPlan(e) {
    const planId = e.currentTarget.dataset.plan
    const plan = this.data.plans.find(p => p.id === planId)
    this.setData({
      selectedPlan: planId,
      selectedPrice: plan.price
    })
  },

  // 发起支付
  handlePay() {
    const { selectedPlan, plans } = this.data
    const plan = plans.find(p => p.id === selectedPlan)

    if (!plan) {
      wx.showToast({
        title: '请选择套餐',
        icon: 'none'
      })
      return
    }

    this.setData({ paying: true })

    // 获取token
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      this.setData({ paying: false })
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/login/login'
        })
      }, 1500)
      return
    }

    // 调用后端创建订单
    wx.request({
      url: app.globalData.apiUrl + '/api/payment/create',
      method: 'POST',
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      data: {
        amount: plan.price,
        description: `${plan.name} - ${plan.duration}`,
        plan_type: plan.id  // 传递套餐类型: monthly 或 yearly
      },
      success: (res) => {
        console.log('创建订单成功:', res.data)

        if (res.data.code === 200) {
          const paymentData = res.data.data.payment

          // 调起微信支付
          wx.requestPayment({
            timeStamp: paymentData.timeStamp,
            nonceStr: paymentData.nonceStr,
            package: paymentData.package,
            signType: paymentData.signType,
            paySign: paymentData.paySign,
            success: (res) => {
              console.log('支付成功:', res)
              wx.showToast({
                title: '支付成功',
                icon: 'success',
                duration: 2000
              })

              // 延迟返回上一页
              setTimeout(() => {
                wx.navigateBack()
              }, 2000)
            },
            fail: (err) => {
              console.error('支付失败:', err)
              if (err.errMsg.includes('cancel')) {
                wx.showToast({
                  title: '支付已取消',
                  icon: 'none'
                })
              } else {
                wx.showToast({
                  title: '支付失败',
                  icon: 'none',
                  duration: 3000
                })
              }
            },
            complete: () => {
              this.setData({ paying: false })
            }
          })
        } else {
          wx.showToast({
            title: res.data.message || '创建订单失败',
            icon: 'none'
          })
          this.setData({ paying: false })
        }
      },
      fail: (err) => {
        console.error('请求失败:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        this.setData({ paying: false })
      }
    })
  },

  // 返回上一页
  goBack() {
    wx.navigateBack()
  }
})
