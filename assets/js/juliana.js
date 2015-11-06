/*
 * Juliana by Cas Ebbers <cjaebbers@gmail.com>
 * Front-end application for bar personnel, in Abscint Bars
 * supporting Alexia
 */

// src:http://phpjs.org/functions/date/
_pad = function (n, c) {
    n = n.toString();
    return n.length < c ? _pad('0' + n, c, '0') : n;
};

/*
 * LOG - logger status
 */
Log = {
    log: function (text) {
        var d = new Date();
        var h = d.getHours();
        var m = d.getMinutes();
        if (h < 10) h = '0' + h;
        if (m < 10) m = '0' + m;
        $('#log-table').append('<tr><td width="20%">[' + h + ':' + m + ']</td><td>' + text + '</td></li>');
    }
};

State = {
    SALES: 0,
    PAYING: 1,
    ERROR: 2,
    CHECK: 3,
    MESSAGE: 4,

    current: this.SALES,
    toggleTo: function (newState, argument) {
        switch (newState) {
            case this.SALES:
                console.log('Changing to SALES...');
                this.current = this.SALES;

                clearInterval(Receipt.counterInterval);
                Receipt.clear();
                $('#payment-receipt').html('');
                $('#countdownbox').show();

                this._hideAllScreens();
                $('#cashier-screen').show();
                break;
            case this.CHECK:
                console.log('Changing to CHECK...');
                this.current = this.CHECK;
                break;
            case this.PAYING:
                console.log('Changing to PAYING...');
                this.current = this.PAYING;
                this._hideAllScreens();

                var receipt = Receipt.getReceipt();
                var receiptHTML = '';
                var total = 0;
                for (var i = 0; i < receipt.length; i++) {
                    receiptHTML += '<tr>';
                    receiptHTML += '<td>' + Settings.products[receipt[i].product].name + '</td>';
                    receiptHTML += '<td>' + receipt[i].amount + '</td>';
                    receiptHTML += '<td>&euro;' + (receipt[i].price / 100).toFixed(2) + '</td>';
                    receiptHTML += '</tr>';
                    total += receipt[i].price;
                }
                receiptHTML += '<tr class="active"><td><strong>Totaal:</strong></td><td></td><td><strong>&euro;' + (total / 100).toFixed(2) + '</strong></td></tr>';
                $('#payment-receipt').html(receiptHTML);

                $('#rfid-screen').show();
                break;
            case this.ERROR:
                this.current = this.ERROR;
                this._hideAllScreens();

                $('#current-error').html(argument);

                $('#error-screen').show();
                break;
            case this.MESSAGE:
                console.log('Changing to MESSAGE...');
                this.current = this.MESSAGE;
                this._hideAllScreens();

                $('#current-message').html(argument);
                $('#message-screen').show();
                break;
            default:
                console.log('Error: no known state');
                break;
        }
        $('.btn').attr('draggable', false).on('dragstart', function () {
            return false;
        });
    },

    _hideAllScreens: function () {
        $('#rfid-screen').hide();
        $('#cashier-screen').hide();
        $('#error-screen').hide();
        $('#message-screen').hide();
    }
};

/*
 * NFC SCAN
 */
Scanner = {
    init: function () {
        var scanner = this;
        var socket;

        if (Settings.androidapp) {
            // Juliana app on Android will not connect if a protocol is specified
            socket = new WebSocket('ws://localhost:3000');
        } else {
            // JulianaNFC_C application on Windows will not connect without nfc protocol
            socket = new WebSocket('ws://localhost:3000', 'nfc');
        }

        socket.onmessage = function (event) {
            var rfid = JSON.parse(event.data);
            scanner.action(rfid);
        }

    },
    action: function (rfid) {
        console.log('CurrentState: ' + State.current);
        if (State.current === State.SALES) {
            if (Receipt.getReceipt().length > 0) {
                Receipt.pay(rfid);
            } else {
                console.log('Info: receipt empty');
                Display.set('Please select products!');
            }
        } else if (State.current === State.CHECK) {
            console.log('Requesting check');
            User.check(rfid);
        } else {
            console.log('Error: not on SALES or CHECK screen');
        }
    }
};

/*
 * DISPLAY - upper status line
 */
Display = {
    set: function (text) {
        $('#display').html(text);
    },
    flash: function () {
        $('#display').effect('shake').effect('highlight', {color: '#fcc'})
    }
};

/*
 * RECEIPT - left panel
 */
Receipt = {
    index: 0,
    receipt: [],
    counterInterval: null,
    payData: null,
    add: function (product, quantity) {
        if (State.current !== State.SALES) {
            console.log('Error: not on SALES screen');
            Display.flash();
            return;
        }

        //add product to receipt (visually)
        var desc = $('.tab-sale a[data-product="' + product + '"]').text();
        if (quantity !== 1) desc += ' &times; ' + quantity;

        var price = ((quantity * Settings.products[product].price) / 100).toFixed(2);

        $('#receipt-table').append('<tr data-pid="' + this.index + '"><td width="70%"><a onclick="Receipt.remove($(this).data(\'pid\'));" class="btn btn-danger command" href="#" data-pid="' + this.index + '">X</a><span>' + desc + '</span></td><td>€' + price + '</td></tr>');

        //add product to actual receipt
        this.receipt[this.index] = {
            'product': product,
            'amount': quantity,
            'price': quantity * Settings.products[product].price
        };
        this.index++;

        this.updateTotalAmount();

        Display.set('OK');
    },
    remove: function (index) {
        //remove product from receipt (visually)
        $('#receipt-table').find('tr[data-pid="' + index + '"]').remove();

        //remove product from actual receipt
        this.receipt[index] = undefined;
        this.updateTotalAmount();
    },
    updateTotalAmount: function () {
        // generate total
        var sum = 0;
        for (var i = 0; i < this.receipt.length; i++) {
            if (this.receipt[i]) {
                sum += this.receipt[i].amount * Settings.products[this.receipt[i].product].price;
            }
        }
        var amount = (sum / 100).toFixed(2);
        $('#receipt-total').find('input').val('' + amount);
        return sum;
    },
    addText: function (text, quantity) {
        $('#receipt-table').append('<tr><td width="70%">' + text + '</td><td>' + quantity + '</td></tr>');
        Display.set('OK');
    },
    clear: function () {
        $('#receipt-table').empty();
        this.receipt = [];
        this.index = 0;
        this.updateTotalAmount();
    },
    getReceipt: function () {
        //Filter empty entries from the receipt
        var receipt = this.receipt.filter(Boolean);

        var cleanReceipt = [];
        var foundProducts = [];
        for (var i = 0; i < receipt.length; i++) {
            if ($.inArray(receipt[i].product, foundProducts) !== -1) {
                //add to existing product in receipt
                for (var j = 0; j < cleanReceipt.length; j++) {
                    if (cleanReceipt[j].product === receipt[i].product) {
                        cleanReceipt[j].amount += receipt[i].amount;
                        cleanReceipt[j].price += receipt[i].price;
                    }
                }
            } else {
                //First time this product get's added
                //add product to foundProducts and cleanReceipt
                foundProducts.push(receipt[i].product);
                cleanReceipt.push($.extend({}, receipt[i]));
            }
        }
        return cleanReceipt;
    },
    pay: function (rfid) {
        State.toggleTo(State.PAYING);

        console.log('Card scanned. Retrieving userData for: ' + rfid);
        User.retrieveData(rfid, function (result) {
            Receipt.continuePay(result, rfid);
        });

    },
    continuePay: function (userData, rfid) {
        console.log('continuePay was called: ');
        console.log(userData);
        if (!userData) {
            State.toggleTo(State.ERROR, 'RFID card retrieval failed');
        } else if (userData.error) {
            State.toggleTo(State.ERROR, 'Error authenticating: ' + userData.error.message);
        } else {
            /*
             juliana_order_save(
             event_id,
             user_id,
             [{'product': product_id,
             'amount': amount,
             'price': totalprice}]
             );
             */
            console.log('Userdata received correctly. Proceeding to countdown.');

            Receipt.payData = {
                event_id: Settings.event_id,
                user_id: userData.result.user.id,
                purchases: Receipt.getReceipt(),
                rfid_data: rfid
            };

            var countdown = Settings.countdown - 1;
            $('#payment-countdown').text(countdown + 1);
            Receipt.counterInterval = setInterval(function () {
                $('#payment-countdown').text(countdown);
                if (countdown === 0) {
                    Receipt.payNow();
                }
                countdown--;
            }, 1000);
        }
    },
    payNow: function () {
        console.log('Processing payment now.');
        var rpcRequest = {
            jsonrpc: '2.0',
            method: 'juliana.order.save',
            params: Receipt.payData,
            id: 1
        };

        clearInterval(Receipt.counterInterval);
        Receipt.confirmPay(rpcRequest);

    },
    confirmPay: function (rpcRequest) {
        IAjax.request(rpcRequest, function (result) {
            if (result.error) {
                State.toggleTo(State.ERROR, 'Error with payment: ' + result.error);
            } else {
                State.toggleTo(State.SALES);
            }
        });
    },
    cash: function () {
        console.log('Paying cash');
        var sum = Receipt.updateTotalAmount();
        var amount = Math.ceil(sum / 10) * 10;
        State.toggleTo(State.MESSAGE, 'Dat wordt dan &euro; ' + (amount/100).toFixed(2));
    }
};

/*
 * INPUT - processes
 */
Input = {
    prompt: '',
    latch_command: '',
    stroke: function (input) {
        // must be a string
        if (typeof input !== 'string') return;
        // don't allow prepended zeroes
        if (input === '0' && this.prompt === '') return;
        // add to prompt
        this.prompt += input;
        Display.set(this.prompt);
    },
    read: function () {
        // parse the input as integer and pass it on
        return parseInt(this.prompt);
    },
    isEmpty: function () {
        return this.prompt == '';
    },
    reset: function () {
        if (this.latch_command !== '') {
            eval(this.latch_command);
            this.latch_command = '';
        }

        this.prompt = '';
    },
    latch: function (command) {
        this.latch_command = command;
    }
};

/*
 * SALES - individual sales, beverages not paid with a "borrelkaart"
 */
Sales = {
    add: function (product, quantity) {
        // add item to receipt
        quantity = !quantity ? 1 : quantity;

        Receipt.add(product, quantity);
    }
};

User = {
    retrieveData: function (rfid, callback) {
        console.log('RetrieveData called!');
        var data = {
            event_id: Settings.event_id,
            rfid: rfid
        };
        var rpcRequest = {
            jsonrpc: '2.0',
            method: 'juliana.rfid.get',
            params: data,
            id: 1
        };
        console.log('Sending request: ' + JSON.stringify(rpcRequest));
        IAjax.request(rpcRequest, callback);
    },
    check: function (rfid) {
        console.log('Card scanned. Retrieving userData for: ' + rfid);
        User.retrieveData(rfid, function (data) {
            Display.set('?');
            User.continueCheck(data.result.user);
        });
    },
    continueCheck: function (user) {
        console.log(JSON.stringify(user));
        var rpcRequest = {
            jsonrpc: '2.0',
            method: 'juliana.user.check',
            params: {event_id: Settings.event_id, user_id: user.id},
            id: 1
        };
        IAjax.request(rpcRequest, function (data) {
            State.toggleTo(State.MESSAGE, user.first_name + " heeft op deze borrel al &euro;" + (data.result / 100).toFixed(2) + " verbruikt.");
        });
    }
};

IAjax = {
    request: function (data, callback) {
        console.log('IAjax sent: ' + JSON.stringify(data));
        var settings = {
            data: JSON.stringify(data),
            url: Settings.api_url,
            dataType: "json",
            type: "POST",
            success: function (result) {
                console.log('Succesfully sent: ' + result);
                if (callback) {
                    console.log('Response received: calling callback.');
                    callback(result);
                }
            },
            error: function (error) {
                var result = JSON.parse(error.responseText);
                console.log('IAjax request failed');
                State.toggleTo(State.ERROR, result.error.message);
            }
        };
        jQuery.ajax(settings);
    }
};

$(function () {
    Scanner.init();

    State.toggleTo(State.SALES);

    $('#welcome').modal();

    $('.btn-keypad').click(function () {
        Input.stroke($(this).html());
    });

    $(document).keypress(function (event) {
        if(event.key >= '0' && event.key <= '9')
            Input.stroke(event.key);
    });

    $('.command').click(function () {
        var reset = true;

        switch ($(this).data('command')) {
            case 'clear':
                Display.set('?');
                break;
            case 'sales':
                Sales.add($(this).data('product'), Input.read());
                break;
            case 'cancel':
                Display.set('?');
                State.toggleTo(State.SALES);
                Receipt.clear();
                break;
            case 'check':
                State.toggleTo(State.CHECK);
                Display.set('Scan een kaart');
                break;
            case 'cash':
                Receipt.cash();
                break;
            case 'cancelPayment':
                State.toggleTo(State.SALES);
                break;
            case 'payNow':
                Receipt.payNow();
                break;
            case 'ok':
                State.toggleTo(State.SALES);
                break;
            default:
                Display.set('ongeimplementeerde functie');
                Display.flash();
                break;
        }

        if (reset) Input.reset();
    });
});
