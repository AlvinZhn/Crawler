var arrivalRange = new AMap.ArrivalRange();
var x, y, t = 60, vehicle = "SUBWAY,BUS";
var workAddress, workMarker, source
var rentInfo = {};
var rentMarkerArray = [];
var polygonArray = [];
var amapTransfer;

var infoWindow = new AMap.InfoWindow({
    offset: new AMap.Pixel(0, -30)
})

var apiMashupRentInfo = function (site, form, callback) {
    var path = `/api/mashup/${site}/all`
    ajax('POST', path, form, callback)
}

var addMarkerByAddress = function (data) {
    var markerOptions = {
        map: map,
        title: data.location,
        icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
        position: [data.lng, data.lat]
    }
    rentMarker = new AMap.Marker(markerOptions);
    rentMarkerArray.push(rentMarker);
    rentMarker.content = `
        <div>房源：<a target = '_blank' href='${data.url}'>${data.title}</a><div>
        <div>大小：${data.room_type}, ${data.size}<div>
        <div>价格：${data.price}<div>
        <div>信息抓取时间：${data.created_time}<div>`
    rentMarker.on('click', function (e) {
        infoWindow.setContent(e.target.content);
        infoWindow.open(map, e.target.getPosition());
        if (amapTransfer) amapTransfer.clear();
        amapTransfer = new AMap.Transfer({
            map: map,
            city:'杭州市',
            policy: AMap.TransferPolicy.LEAST_TIME,
            panel: 'transfer-panel'
        });
        amapTransfer.search([{
            keyword: workAddress
        }, {
            keyword: data.location
        }], function (status, result) {
        })
    });
}

var delRentLocation = function () {
    if (rentMarkerArray) map.remove(rentMarkerArray);
    rentMarkerArray = [];
}

var loadRentLocation = function (allData) {
    delRentLocation();
    allData.forEach(function (element, index) {
        addMarkerByAddress(element);
    });
}

var filterDataInArea = function (allData) {
    var coordinateInArea = function (lng, lat) {
        var flag
        for (let i = 0; i < polygonArray.length; i++) {
            var area = polygonArray[i]
            if (area.contains([lng, lat])){
                flag = true
                break
            }    
        }
        return flag
    }
    for (const key in allData) {
        rentInfo[key] = new Array
        allData[key].forEach(function (element, index) {
            var lng = element.lng
            var lat = element.lat
            if (coordinateInArea(lng, lat)) {
                rentInfo[key].push(element)
            }
        })
    }
}

var loadPolygonArea = function () {
    var lngMax, latMax, lngMin, latMin
    lngMax = parseFloat(polygonArray[0].getBounds().northeast.lng)
    lngMin = parseFloat(polygonArray[0].getBounds().southwest.lng)
    latMax = parseFloat(polygonArray[0].getBounds().northeast.lat)
    latMin = parseFloat(polygonArray[0].getBounds().southwest.lat)
    polygonArray.forEach(function (element, index) {
        var lngMaxNew = parseFloat(element.getBounds().northeast.lng)
        var lngMinNew = parseFloat(element.getBounds().southwest.lng)
        var latMaxNew = parseFloat(element.getBounds().northeast.lat)
        var latMinNew = parseFloat(element.getBounds().southwest.lat)
        if (lngMaxNew > lngMax) {
            lngMax = lngMaxNew
        }
        if (lngMinNew < lngMin) {
            lngMin = lngMinNew
        }
        if (latMaxNew > latMax) {
            latMax = latMaxNew
        }
        if (latMinNew < latMin) {
            latMin = latMinNew
        }
    })
    return {
        lngMax: lngMax, 
        latMax: latMax,
        lngMin: lngMin, 
        latMin: latMin
    }
}

var loadWorkRange = function (x, y, t, color, v) {
    arrivalRange.search([x, y], t, function (status, result) {
        if (result.bounds) {
            for (var i = 0; i < result.bounds.length; i++) {
                var polygon = new AMap.Polygon({
                    map: map,
                    fillColor: color,
                    fillOpacity: "0.4",
                    strokeColor: '#00FF00',
                    strokeOpacity: "0.8",
                    strokeWeight: 1
                });
                polygon.setPath(result.bounds[i]);
                polygonArray.push(polygon);
            }
            var area = loadPolygonArea()
            var form = {
                'lngMax': area.lngMax,
                'lngMin': area.lngMin,
                'latMax': area.latMax,
                'latMin': area.latMin,
            }
            apiMashupRentInfo('renting', form, function (r) {
                var response = JSON.parse(r)
                filterDataInArea(response)
                if (source != undefined) {
                    loadRentLocation(rentInfo[source])
                }
            })              
        }      
    }, {
        policy: v
    });
}

var loadWorkMarker = function (x, y, locationName) {
    workMarker = new AMap.Marker({
        map: map,
        title: locationName,
        icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
        position: [x, y]

    });
}

var delWorkLocation = function () {
    if (polygonArray) map.remove(polygonArray);
    if (workMarker) map.remove(workMarker);
    polygonArray = [];
}

var loadWorkLocation = function () {
    delWorkLocation();
    var geocoder = new AMap.Geocoder({
        city:'杭州',
        radius: 1000
    });

    geocoder.getLocation(workAddress, function (status, result) {
        if (status === "complete" && result.info === 'OK') {
            var geocode = result.geocodes[0];
            x = geocode.location.getLng();
            y = geocode.location.getLat();
            loadWorkMarker(x, y);
            loadWorkRange(x, y, t, "#3366FF", vehicle);            
            map.setZoomAndCenter(12, [x, y]);
        }
    })
}

var bindEventWorkLocationSelected = function () {
    var auto = new AMap.Autocomplete({
        input: "work-location"
    });
    AMap.event.addListener(auto, "select", function (e) {
        workAddress = e.poi.name;
        loadWorkLocation();
    });
}

var bindEventSelectVehicle = function () {
    $('.vehicle').bind('click', function (e) {
        var target = $(e.target)
        if (target.hasClass('bus-sub')) {
            $($('.bus-sub')[0]).prop('checked', true)                
            $($('.bus')[0]).prop('checked', false)
            vehicle = $('.bus-sub')[0].value         
        } else if (target.hasClass('bus')) {
            $($('.bus')[0]).prop('checked', true)                
            $($('.bus-sub')[0]).prop('checked', false)
            vehicle = $('.bus')[0].value         
        }
        loadWorkLocation()
    })
}

var bindEventSelectSource = function () {
    $('#id-source').change(function () {
        source = $('#id-source option:selected').val()
        if (rentInfo[source] != undefined) {
            loadRentLocation(rentInfo[source])
        }
    })
}

var bindEventClearTransfer = function () {
    $('#container').bind('click', function (e) {
        $('#container .amap-info-close').off('click').on('click', function (r) {
            if (amapTransfer) amapTransfer.clear();
        })
    })
}

var initMap = function () {
    map = new AMap.Map('container', {
        resizeEnable: true,
        zoom: 11,
        center: [120.180895, 30.281714]
    });

    var scale = new AMap.Scale();
    map.addControl(scale);
}

var bindEvents = function () {
    bindEventWorkLocationSelected()
    bindEventSelectVehicle()
    bindEventSelectSource()
    bindEventClearTransfer()
}

var __main = function () {
    initMap()
    bindEvents()
}

__main()