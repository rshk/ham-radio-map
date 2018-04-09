(function() {

    function httpGet(url, onSuccess, onFailure) {
        let xhr = new XMLHttpRequest();
        xhr.open('GET', url);
        // xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                onSuccess(xhr.responseText, xhr);
                // L.geoJSON(JSON.parse(xhr.responseText)).addTo(map);
            }
            else {
                onFailure(xhr.responseText, xhr);
            }
        };
        xhr.send();
    }

    function E(name, attrs) {
        var el = document.createElement(name);
        attrs = attrs || {};
        if (attrs.text) {
            el.textContent = attrs.text;
            delete attrs.text;
        }
        if (attrs.children) {
            for (let child of attrs.children) {
                el.appendChild(child);
            }
            delete attrs.children;
        }
        if (attrs) {
            Object.assign(el, attrs);
        }
        return el;
    }

    function T(text) {
        return document.createTextNode(text);
    }

    function fmtFreq(num) {
        var numTxt = Math.floor(Math.abs(num)).toString();

        var reg = /(\d+)(\d{3})/;
        while (reg.test(numTxt)) {
            numTxt = numTxt.replace(reg, '$1.$2');
        }
        return numTxt;
    }

    function fmtOffset(num) {
        var sign = num < 0 ? '-' : '+';
        return sign + fmtFreq(num);
    }

    function leftPad(text, size, char) {
        while (text.length < size) {
            text += char;
        }
        return text;
    }

    var map = L.map('map'); //.setView([51.505, -0.09], 13);
    window.leafletMap = map;  // for debugging

    // Fit Ireland
    map.fitBounds(new L.LatLngBounds({
        // NorthEast
        lat: 55.56592203025787,
        lng: -5.273437500000001,
    },{
        // SouthWest
        lat: 51.227527905265006,
        lng: -10.689697265625002,
    }));

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    /*
     * L.marker([51.5, -0.09]).addTo(map)
     *  .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
     *  .openPopup(); */

    // EI repeaters --------------------------------------------------

    var repeatersLayer = L.geoJSON(null, {
        // style: function (feature) {
        //     return {color: feature.properties.color};
        // }
    }).bindPopup(function (layer) {
        var container = E('div');
        container.appendChild(E('h2', {text: layer.feature.properties.callsign}));


        container.appendChild(E('dl', {
            children: [
                E('dt', {text: 'Channel'}),
                E('dd', {text: layer.feature.properties.channel}),

                E('dt', {text: 'Output frequency'}),
                E('dd', {children: [E('code', {text: fmtFreq(layer.feature.properties.freqout)})]}),

                E('dt', {text: 'Input frequency'}),
                E('dd', {children: [E('code', {text: fmtFreq(layer.feature.properties.freqin)})]}),

                E('dt', {text: 'Offset'}),
                E('dd', {children: [E('code', {text: fmtOffset(
                    layer.feature.properties.freqin - layer.feature.properties.freqout)})]}),

                E('dt', {text: 'Access'}),
                E('dd', {text: layer.feature.properties.access}),

                E('dt', {text: 'Location'}),
                E('dd', {text: layer.feature.properties.loc_name}),

                E('dt', {text: 'Locator'}),
                E('dd', {children: [E('code', {text: layer.feature.properties.locator})]}),

                E('dt', {text: 'Notes'}),
                E('dd', {text: layer.feature.properties.notes}),
            ]
        }))
        return container;
    }).addTo(map);

    httpGet('./data/ei-repeaters.json', function(responseText) {
        var data = JSON.parse(responseText);
        repeatersLayer.addData(data);
    });

})();
