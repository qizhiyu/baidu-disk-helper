
function renderStatus(statusText) {
    document.getElementById('status').textContent = statusText;
}

/**
 * @param {url} listing Url, could be in many forms
 * verify listing url and return Id if found, otherwise 0
 */
function extractListingId(url) {
    //http://www.trademe.co.nz/property/residential-property-for-sale/auction-1249809896.htm
    //http://www.trademe.co.nz/Browse/Listing.aspx?id=1256906561
    //http://www.trademe.co.nz/1256906561
    var patt = /trademe\D+(\d+)/i;
    var matchs = patt.exec(url);
    if (matchs == null || matchs.length != 2)
        return 0;
    return Number(matchs[1]);
}

function getHistory(url, callback, errorCallback) {
    var id = extractListingId(url);
    if (id == 0) {
        errorCallback("Invalid Url");
        return;
    }

    //TODO: load history from API
    var searchUrl = "http://192.168.1.9/bo" + "/api/houses/" + String(id);
    var x = new XMLHttpRequest();
    x.open('GET', searchUrl);
    // The Google image search API responds with JSON, so let Chrome parse it.
    x.responseType = 'json';
    x.onload = function () {
        // Parse and process the response from Google Image Search.
        var response = x.response;
        if (!response) {
            errorCallback('Listing not found!');
            return;
        }
        callback(response);
    };
    x.onerror = function () {
        errorCallback('Network error.');
    };
    x.send();
}

function createElement() {
    var table = document.getElementById('ListingAttributes');
    var row = table.insertRow(0);
    var cell1 = document.createElement('th');
    cell1.innerHTML = "Price History:";
    row.appendChild(cell1);
    var cell2 = row.insertCell(1);
    return cell2;
}

function render(response) {
    //API backward compatability support
    if (response.History != null && response.History.length > 0)
        renderStringResult(response.History);
    else
        renderArrayResult(response.HouseHistories)
}

function renderStringResult(history) {
    //clear display area
    var status = createElement();
    status.innerHTML = "";
    if (history == null || history.length == 0)
        return;

    status.innerHTML = history.replace("\t", "&nbsp;").replace("\n", "<br>");
}

function renderArrayResult(results) {
    //clear display area
    var status = createElement();
    status.innerHTML = "";
    if (results == null || results.length == 0)
        return;

    var text = "";
    for (var i = 0; i < results.length; i++) {
        text += String(results[i].ChangedAt) + "&nbsp;" + results[i].Price + "<br>";
    }
    status.innerHTML = text;
}

getHistory(location, render, renderStatus);