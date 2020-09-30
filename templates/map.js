$(function() {

var OPENAPI_KEY = '11PtzPKFz%2F8XXCD0NO7lxl7%2Fb7VDNEFtTpbcvYi2vzDBicQpPAz5o7auO3VtzGUZcfibeIh0aWgRVOeoL6I06A%3D%3D';
    // ALL YOUR CODE INSIDE

var map = new naver.maps.Map('naverMap', { // naverMap 값은 div 의 id 값
	center : new naver.maps.LatLng(35.9, 127.093031), // 지도 중앙 위치 : 위도, 경도 설정
	zoom : 8, // 줌 설정 : 5~22, 수치가 클수록 지도 확대(줌인), 이 옵션 생략시 기본값 9
    zoomControl : true, // 줌 컨트롤 표시 (기본값 표시안함)
	zoomControlOptions : { // 줌 컨트롤 왼쪽 위로 위치 설정
        position : naver.maps.Position.TOP_LEFT // 왼쪽 위로 설정값
    },
    mapTypeControl: true,
	mapTypeControlOptions: {
        style: naver.maps.MapTypeControlStyle.BUTTON,
        position: naver.maps.Position.TOP_RIGHT
    },
    logoControl: true,
    logoControlOptions: {
        position: naver.maps.Position.BOTTOM_LEFT
    },
    useStyleMap: true,
    disableKineticPan: false
});

// 로케이션 찾기 함수

function onSuccessGeolocation(position) {
    var location = new naver.maps.LatLng(position.coords.latitude,
                                         position.coords.longitude);
    var marker = new naver.maps.Marker({
        position: location,
        map: map
    })
    console.log(location);
    console.log('1');
    var changedCoord = naver.maps.UTMK.fromLatLngToUTMK(location);

    console.log(changedCoord.x);

    // 마커 정보창
    var contentString = [
        '<div class="iw_inner" style="padding:10px;min-width:200px;line-height:150%;">',
		'<h4 style="margin-top:5px;">현재 위치<span class="close">&times;</span></h4>',
        '<br /><center><a type="button" class="a_class" target="_blank" rel="noopener noreferrer" href="https://www.ev.or.kr/mobile/mevloc?gubun=1&curX='+changedCoord.x+'&curY='+changedCoord.y+'&poNm=1">'+
        '<img src="./img/core-img/favicon.png" width="23" height="23" alt="evmark" class="evmark_search"> Near Charging Stations</a><br /><br />'+
        '<a type="button" class="b_class" target="_blank" rel="noopener noreferrer" href="https://map.naver.com/v5/search/전기차충전소?15,0,0,0,dh">'+
        '<img src="./img/core-img/navermap1.png" width="20" height="20" alt="navermark" class="evmark_search"> Searching on Naver</a></center>',
		'</div>'
    ].join('');
    
    var infowindow = new naver.maps.InfoWindow({
    content: contentString
    });
    
    infowindow.open(map, marker);

    naver.maps.Event.addListener(marker, "click", function(e) {
    if (infowindow.getMap()) {
        infowindow.close();
    } 
    else {
        infowindow.open(map, marker);
    }
    });

    $(function(){       
        $(".close").click(function(){
            infowindow.close();
         });
    });

    map.setCenter(location); // 얻은 좌표를 지도의 중심으로 설정합니다.
    map.setZoom(14); // 지도의 줌 레벨을 변경합니다.

}



function onErrorGeolocation() {
    var center = map.getCenter();
}
// 로케이션 함수 끝

// search 버튼 현위치 뽑아오기
$('.rehomes-search-btn').on("click", function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(onSuccessGeolocation, onErrorGeolocation);
    } 
    else {
        var center = map.getCenter();
        
    }
});

var infoWindow = new naver.maps.InfoWindow({
    anchorSkew: true
});


map.setCursor('pointer');

function searchCoordinateToAddress(latlng) {

infoWindow.close();
// 위치 뽑고 팝업 끝

// 주소 받아오기
naver.maps.Service.reverseGeocode({
	coords: latlng,
	orders: [
		naver.maps.Service.OrderType.ADDR,
		naver.maps.Service.OrderType.ROAD_ADDR
	].join(',')}, 
	function(status, response) {
	if (status === naver.maps.Service.Status.ERROR) {
		return alert('Something Wrong!');
	}



	var items = response.v2.results,
		address = '',
		htmlAddresses = [];
	var coords = latlng
	var latlng_UTM = naver.maps.UTMK.fromLatLngToUTMK( coords );
	var split = String(latlng_UTM).split(',');
	var lat_UTM = split[0].split('(')[1];
	var lng_UTM = split[1].split(')')[0];

	for (var i=0, ii=items.length, item, addrType; i<ii; i++) {
		item = items[i];
		address = makeAddress(item) || '';
    }
    console.log(address);
    console.log(latlng_UTM);
    //xhr.send('');
    console.log("performing search");

    /** 
    $.ajax({
        url: url + queryParams,
        method: "GET",
        success: function(data) {
            console.log(data)
        }
    }) **/

    /** tmpurl = "https://www.ev.or.kr/mobile/mevloc?gubun=1&curX=" + lat_UTM + "&curY=" + lng_UTM + "&poNm=1"
    $.ajax({
        url: tmpurl,
        method: "GET",
        success: function (data) {
         robj = $(data);
         stations = robj.find("#data_list ul li");
         var i = 0;
         while (i < stations.length) {
            station = stations[i];
            station_script = $(station).find("div.ev_area_info > script");
            if ($(station_script[0]).text() == "document.write(getStatMSpan('2'));") {
               urls = $(station).find("div.ev_add_info div.sub_group div.location_info div.location_bg div a");
               localisation_text = $(urls[0]).attr('onclick').split("'")[3];
               console.log(localisation_text);
               break;
            }
            i++;
         }
         if (i >= stations.length) {
            console.error("no available station");
         }
        }
    }); **/
    console.log(lat_UTM);
    console.log(lng_UTM);
	infoWindow.setContent([
		'<div class="search_div" style="padding:10px;min-width:200px;line-height:150%;">',
		'<h4 style="margin-top:5px;">Options<span class="close">&times;</span></h4>',
		htmlAddresses.join('<br />'),
        '<br /><center><a type="button" class="a_class" target="_blank" rel="noopener noreferrer" href="https://www.ev.or.kr/mobile/mevloc?gubun=1&curX='+lat_UTM+'&curY='+lng_UTM+'&poNm=1">'+
        '<img src="./img/core-img/favicon.png" width="23" height="23" alt="evmark" class="evmark_search"> Near Charging Stations</a><br /><br />'+
        '<a type="button" class="b_class" target="_blank" rel="noopener noreferrer" href="https://map.naver.com/v5/search/전기차충전소?c='+ coords.x + ',' + coords.y +',15,0,0,0,dh">'+
        '<img src="./img/core-img/navermap1.png" width="20" height="20" alt="navermark" class="evmark_search"> Searching on Naver</a></center>',
		'</div>'
	].join('\n'));

    infoWindow.open(map, latlng);

    $(function(){       
        $(".close").click(function(){
            infoWindow.close();
         });
    });
    map.setCenter(latlng);
});
}




function initGeocoder() {
    map.addListener('click', function(e) {
        searchCoordinateToAddress(e.coord);
    });

    $('#address').on('keydown', function(e) {
        var keyCode = e.which;

    });
}
// makeAddress !!!
function makeAddress(item) {
    if (!item) {
        return;
    }

    var name = item.name,
        region = item.region,
        land = item.land,
        isRoadAddress = name === 'roadaddr';

    var sido = '', sigugun = '', dongmyun = '', ri = '', rest = '';

    if (hasArea(region.area1)) {
        sido = region.area1.name;
    }

    if (hasArea(region.area2)) {
        sigugun = region.area2.name;
    }

    if (hasArea(region.area3)) {
        dongmyun = region.area3.name;
    }

    if (hasArea(region.area4)) {
        ri = region.area4.name;
    }

    if (land) {
        if (hasData(land.number1)) {
            if (hasData(land.type) && land.type === '2') {
                rest += '산';
            }

            rest += land.number1;

            if (hasData(land.number2)) {
                rest += ('-' + land.number2);
            }
        }

        if (isRoadAddress === true) {
            if (checkLastString(dongmyun, '면')) {
                ri = land.name;
            } else {
                dongmyun = land.name;
                ri = '';
            }

            if (hasAddition(land.addition0)) {
                rest += ' ' + land.addition0.value;
            }
        }
    }

    return [sido, sigugun, dongmyun, ri, rest].join(' ');
}

function hasArea(area) {
    return !!(area && area.name && area.name !== '');
}

function hasData(data) {
    return !!(data && data !== '');
}

function checkLastString (word, lastString) {
    return new RegExp(lastString + '$').test(word);
}

function hasAddition (addition) {
    return !!(addition && addition.value);
}

naver.maps.onJSContentLoaded = initGeocoder;


console.log("map loaded", map);
});