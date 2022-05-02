var socket = io('beta.ia.utwente.nl:21382');
socket.emit('new client', "Juliana");

var pStart = Settings.products[1].price / 100;
var pMax = 0.80;
var pMin = 0.20;
var pDelta = 0.05;
var pMulti = 0.5;

var p = pStart;

var lastAdvertisedPrice = parseInt(pStart * 100);

function newPrice() {
  var cents = Math.round(p * 100);
  Settings.products[1].price = cents;

  if(cents != lastAdvertisedPrice) {
    var diff;
    var string = (cents / 100).toFixed(2).replace('.', ',');
    string += ' ';
    if (cents >= lastAdvertisedPrice) {
      string += '+';
      diff = (cents - lastAdvertisedPrice) / lastAdvertisedPrice;
    } else {
      string += '-';
      diff = (lastAdvertisedPrice - cents) / lastAdvertisedPrice;
    }
    string += (diff * 100).toFixed(1).replace('.', ',');
    string += '%';

    socket.emit('new price', string);
    lastAdvertisedPrice = cents;
  }
}

function reducePrice() {
  p = p - (pDelta * ((p / pMin) - 1));

  if(p < pMin) {
    p = pMin;
  }

  newPrice();
}

function increasePrice(numBeers) {
  p = p + (pDelta * (numBeers ** pMulti));

  if(p > pMax) {
    p = pMax;
  }

  newPrice();
}

setInterval(reducePrice, 60 * 1000);
