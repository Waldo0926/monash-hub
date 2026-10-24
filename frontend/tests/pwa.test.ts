import { describe, expect, it } from 'vitest'
import { detectPlatform } from '../composables/usePwa'

const UA = {
  iphoneSafari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1',
  iphoneChrome: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/140.0.0.0 Mobile/15E148 Safari/604.1',
  iphoneWechat: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.60(0x18003c2f) NetType/WIFI Language/zh_CN',
  androidChrome: 'Mozilla/5.0 (Linux; Android 15; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36',
  androidWechat: 'Mozilla/5.0 (Linux; Android 14; 23127PN0CC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300333 MMWEBSDK/20240802 MicroMessenger/8.0.50.2701(0x28003253) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
  androidHuawei: 'Mozilla/5.0 (Linux; Android 12; HarmonyOS; NOH-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 HuaweiBrowser/15.0.4.312 Mobile Safari/537.36',
  androidQQ: 'Mozilla/5.0 (Linux; Android 14; V2309A) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 V1_AND_SQ_9.0.90_7220_YYB_D QQ/9.0.90.17630 NetType/WIFI',
  macChrome: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

describe('detectPlatform', () => {
  it('sends iPhone readers to the Safari share menu, whatever browser they use', () => {
    expect(detectPlatform(UA.iphoneSafari)).toBe('ios')
    expect(detectPlatform(UA.iphoneChrome)).toBe('ios')
  })

  it('tells WeChat readers to open the page in a browser first, on either phone', () => {
    expect(detectPlatform(UA.iphoneWechat)).toBe('wechat')
    expect(detectPlatform(UA.androidWechat)).toBe('wechat')
  })

  it('treats the QQ app as an in-app browser but not a phone maker\'s own browser', () => {
    expect(detectPlatform(UA.androidQQ)).toBe('inapp')
    expect(detectPlatform(UA.androidHuawei)).toBe('android')
  })

  it('knows Android and desktop', () => {
    expect(detectPlatform(UA.androidChrome)).toBe('android')
    expect(detectPlatform(UA.macChrome)).toBe('desktop')
  })
})
