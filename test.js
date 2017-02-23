function test() {
    testExtractListingId();
    testRenderResult();
}

function testExtractListingId() {
    var input = ["http://www.trademe.co.nz/property/residential-property-for-sale/auction-1249809896.htm",
            "http://www.trademe.co.nz/Browse/Listing.aspx?id=1256906561",
            "http://www.trademe.co.nz/1256906561",
            "http://www.trademe.co.nz/antiques-collectables"
    ];
    var expect = [1249809896, 1256906561, 1256906561, 0];
    for (var i = 0; i < input.length;i++) {
        if (extractListingId(input[i]) != expect[i])
            console.log("Error in testExtractListingId: " + input);
    }
}

function testRenderResult() {
    var result = {
        "HouseHistories": [
          {
              "HouseHistoryId": 17154,
              "HouseId": 1262288115,
              "Price": "Price by negotiation",
              "LastPrice": null,
              "CreatedAt": "2017-02-15T21:50:50.613",
              "ChangedAt": "2017-02-14T14:59:16.28"
          }
        ],
        "HouseId": 1262288115,
        "Title": "A Family Home That Offers It All",
        "Address": "6 Deane Avenue, Titirangi, Waitakere City",
        "Price": "Price by negotiation",
        "Room": "4",
        "BathRoom": "2",
        "ListedAt": "2017-02-14T14:45:00",
        "Auction": null,
        "Land": null,
        "PropertyType": "House",
        "Agent": "Agent's\r\n                    details\n\n\n\n\n\nSteve Isbill\n\n(09) 8397469\n(027) 4927548\n\n\n\n\n\n\n\n\nHarveys Te Atatu - Elysium Realty Ltd MREINZ, Licensed Agent (REAA 2008)\n(09) 8346155\n\n\nOffice's other listings\nView their website",
        "Wording": "\r\n    \r\n    If you are seeking a fantastic, spacious family home with spectacular views, offering real privacy, plenty of garaging and storage, then look no further. \r\n \r\nCome along and discover this massive, extensive timber bungalow set commandingly on a full, freehold site offering striking elevated views of the Waitakere Ranges while being neatly positioned in a quaint, private cul de sac location. \r\n \r\nComprising of four bedrooms, a huge family room with those stunning views, a large bathroom and a second lounge with an ample, secluded decked area, makes it the perfect place for those who like to entertain in privacy. \r\n \r\nOn the lower level, with internal access, is the extensive garaging that is clean and tidy, a second shower and toilet, not to mention the generously sized workshop and storage area. \r\n \r\nPlus, for those that love to renovate it's a wonderful property that you could easily get your teeth into, stamp your mark on and make some improvements to modernise and add real value. \r\n \r\nFor guaranteed easy commuting it is set in one of the most popular streets on the city side of Titirangi Village and being surrounded by excellent schooling, this fantastic home is sure to be extremely popular. \r\n \r\nContact Steve today. \r\n \r\nSET DATE OF SALE Closes 4pm, Wednesday 8 March 2017 (unless sold prior)\r\nAgency reference #: TAT3441\r\n    \r\n    \r\n    \r\n    \r\n    \r\n    \r\n    \r\n",
        "Created": "2017-02-14T14:59:16.28",
        "Url": "/property/residential-property-for-sale/auction-1262288115.htm",
        "ImageUrl": "http://trademe.tmcdn.co.nz/photoserver/med/556169277.jpg",
        "Feature": " feature highlight",
        "History": null,
        "LastVisit": "2017-02-15T21:34:59.617"
    };
    var output = "2017-02-14T14:59:16.28&nbsp;Price by negotiation<br>";

    var status = document.getElementById('status');
    if (status == null){
        var div = document.createElement('div');
        document.body.appendChild(div);
        div.id = 'status';
        div.style.position = 'fixed';
        div.style.top = '50%';
        div.style.left = '50%';
        div.style.width = '100%';
        div.style.height = '100%';
        div.style.backgroundColor = 'red';
    }

    renderResult(result.HouseHistories);
    status = document.getElementById('status');

    if (status.innerHTML != output)
        console.log("Error in testRenderResult" );

}