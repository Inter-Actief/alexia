const socket = io('beta.ia.utwente.nl:21382');
socket.emit('new client', "Juliana");
console.log(`Connected to Wallstreet websocket`)

const linkToBeerPrice = [2, 485]; // Make sure sodas can't get more expensive than beer
const beerProductId = 1;
const products = [
    {id: 1, pMax: 1.00, pMin: 0.25},  // Grolsch
    {id: 2, pMax: 1.00, pMin: 0.25},  // Cola/Fanta
    {id: 485, pMax: 1.00, pMin: 0.25},  // Fuze Tea (big)
    {id: 296, pMax: 2.60, pMin: 0.65},  // Wine glass
];

// Build prices object from products listing above.
let prices = {};
for (const product of products) {
    console.log(`Loading product ${product.id}...`)
    prices[product.id] = {
        pStart: Settings.products[product.id].price / 100,
        pCurrent: Settings.products[product.id].price / 100,
        pLastAdvertised: Settings.products[product.id].price,
        pMax: product.pMax,
        pMin: product.pMin,
    }
}

const pDelta = 0.05;
const pMulti = 0.5;

function advertisePrices() {
    let pricesChanged = false;
    let priceChangeData = {};

    for (const productId in prices) {
        let lastAdvertisedPrice = prices[productId].pLastAdvertised;
        let cents = Settings.products[productId].price;
        let diff;
        let string = (cents / 100).toFixed(2).replace('.', ',');
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

        priceChangeData[productId] = string;

        if (prices[productId].pLastAdvertised !== cents) {
            pricesChanged = true;
        }
    }

    if (pricesChanged) {
        console.log(`Sending new price changes to screen`)
        socket.emit('new prices', priceChangeData);
        for (const productId in prices) {
            prices[productId].pLastAdvertised = Settings.products[productId].price;
        }
    }
}

function reducePrices() {
    for (const productId in prices) {
        let pMin = prices[productId].pMin;
        const pOriginal = prices[productId].pCurrent;
        let pCurrent = prices[productId].pCurrent;
        pCurrent = pCurrent - (pDelta * ((pCurrent / pMin) - 1));

        if(pCurrent < pMin) {
            pCurrent = pMin;
        }

        prices[productId].pCurrent = pCurrent;
        Settings.products[productId].price = Math.round(prices[productId].pCurrent * 100);
        console.log(`Reduced price of ${productId} from ${pOriginal} to ${pCurrent}`)

        // Make sure soda prices also go down if beer price goes down below soda price
        if (productId === beerProductId) {
            for (const sodaId of linkToBeerPrice) {
                if (prices[beerProductId].pCurrent < prices[sodaId].pCurrent) {
                    prices[sodaId].pCurrent = prices[beerProductId].pCurrent;
                    Settings.products[sodaId].price = Settings.products[beerProductId].price;
                    console.log(`Changed price of ${sodaId} to match lower beer price ${prices[beerProductId].pCurrent}`)
                }
            }
        }
    }
    advertisePrices();
}

function increasePrice(countsPerProduct) {
    for (const productId in countsPerProduct) {
        let pMax = prices[productId].pMax;
        const pOriginal = prices[productId].pCurrent;
        let pCurrent = prices[productId].pCurrent;
        pCurrent = pCurrent + (pDelta * (countsPerProduct[productId] ** pMulti));

        if(pCurrent > pMax) {
            pCurrent = pMax;
        }

        prices[productId].pCurrent = pCurrent;
        Settings.products[productId].price = Math.round(prices[productId].pCurrent * 100);
        console.log(`Increased price of ${productId} from ${pOriginal} to ${pCurrent}`)
    }

    // If beer got cheaper than the sodas after increase, make the soda price the same as the beer price
    for (const sodaId of linkToBeerPrice) {
        if (prices[beerProductId].pCurrent < prices[sodaId].pCurrent) {
            prices[sodaId].pCurrent = prices[beerProductId].pCurrent;
            Settings.products[sodaId].price = Settings.products[beerProductId].price;
            console.log(`Changed price of ${sodaId} to match lower beer price ${prices[beerProductId].pCurrent}`)
        }
    }

    advertisePrices();
}

setInterval(reducePrices, 60 * 1000);
