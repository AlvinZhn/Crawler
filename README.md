# Crawler For Douban Movie and etc.

## Python 爬虫及数据处理

### [Online Demo](https://zhangnie.me/#crawler)

- 采用 **request** 发送请求及接收响应，并将返回的内容缓存在本地，通过 **PyQuery** 对数据进行解析与处理，实现对 **豆瓣电影**, **时光网** 和 **58品牌公寓** 的 **分页爬取** 及 **数据清洗**

- 使用 **splinter** 及 **Selenium** 驱动 **无头浏览器**，通过 **cookie 验证登录**，爬取 **知乎** 页面 js 动态生成的 **动态内容**

- 将爬取的 **58品牌公寓** 中房源信息存入数据库，通过调用 **高德地图API** 标出指定条件下的通勤范围，后端将 **数据筛选** 后的房源数据发送到前端并在地图上标记显示，实现便捷找房租

### Demo: 

#### 无头浏览器爬取动态内容

![avatar](https://wx3.sinaimg.cn/large/927e2755gy1frrhxisarcg22g218l7wi.gif)


#### 调用高德地图API标记房源信息

![avatar](https://wx4.sinaimg.cn/large/927e2755gy1frrhxi2fupg21w113qu14.gif)
