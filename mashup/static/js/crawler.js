var apiCrawlerUpdate = function (page, callback) {
    var path = `/api/crawler/renting/gongyu/update?page=${page}`
    ajax('GET', path, '', callback)
}

var apiGeoCoderGet = function (callback) {
    var path = `/api/geocoder/crawler/renting/gongyu`
    ajax('GET', path, '', callback)
}

var sourceSite = function (source) {
    if (source == 'gongyu') {
        var site = 'http://hz.58.com/pinpaigongyu/'
    } else if (source == 'ganji') {
        var site = ''
    }
    return site
}

var autoScroll = function () {
    var scrollTop = e("#id_log_area").scrollHeight
    e("#id_log_area").scrollTop = scrollTop
}

var logClear = function () {
    $('#id_log_area')[0].value = ''
}

var logText = function (text) {
    var logArea = $('#id_log_area')[0]
    var now = '[' + moment().format('HH:mm:ss') + ']  '
    logArea.value += now + text
    autoScroll()
}

var Lng, Lat

var getGeoLocation = function (data) {
    return new Promise(function (resolve, reject) {
        var geocoder = new AMap.Geocoder({
            city: "杭州", //城市，默认：“全国”
            radius: 1000 //范围，默认：500
        });

        geocoder.getLocation(data.location, function (status, result) {
            if (status === 'complete' && result.info === 'OK') {
                geocode = result.geocodes[0];
                Lng = geocode.location.getLng()
                Lat = geocode.location.getLat()
            }
            resolve('ok');
        })
    })
}

var updateGeocoder = async function (data) {
    await getGeoLocation(data)
    $.post(`/api/geocoder/crawler/renting/gongyu/update?id=${data.id}`,
        {
            'lng': Lng,
            'lat': Lat,
        },
        function (data, status) {
            // alert("数据: \n" + data + "\n状态: " + status);
        });
}


var updateCallback = function (site, currentPage) {
    return new Promise(function (resolve, reject) {
        apiCrawlerUpdate(currentPage, function (r) {
            var response = JSON.parse(r)
            if (site == 'renting') {
                var all = response.all
                var newData = response.new_data
                var allData = response.all_data
                all.forEach(function (element, index) {
                    if (element.lat == 0) {
                        updateGeocoder(element)
                    }
                })
                logText(`${newData} data added...\n`)
                logText(`${allData} data in all...\n`)
            }
            resolve('ok');
        })
    })
}

var bindEventUpdate = function () {
    $('.update').on('click', async function (e) {
        $('.modal').addClass('is-active')
        logClear()
        logText('Starting to check update...\n')
        var site = $('.update').data('site')
        var currentPage = 1

        logText(`Connecting ${sourceSite(site)}...\n`)
        logText(`Please wait a moment...\n`)
        await updateCallback(site = 'renting', currentPage)

        logText(`Done...\n`)
    })
    $('.coordinate').on('click', function (e) {
        $('.modal').addClass('is-active')
        logClear()
        logText('Starting to check unfixed data...\n')
        apiGeoCoderGet(function (r) {
            var response = JSON.parse(r)
            var len = response.length
            logText(`${len} error data founded...\n`)
            response.forEach(function (element, index) {
                updateGeocoder(element)
            })
            logText(`Done...\n`)
        })
    })
}

var crawler_bindEvents = function () {
    bindEventUpdate()
}

var crawler_main = function () {
    crawler_bindEvents()
}

crawler_main()