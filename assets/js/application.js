var LOCALE = $('html').attr('lang') || 'en';
var dateformats = {
    nl: 'dd-mm-yyyy',
    en: 'yyyy-mm-dd',
};
var csrftoken = getCookie('csrftoken');

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    }
});

$(function () {

    $('.bartender_availability').change(function () {
        var event_id = $(this).data('event-id');

        $.post('/scheduling/ajax/bartender_availability/', {
            event_id: event_id,
            availability_id: $(this).val()
        }, function (data) {
            $('#assigned_bartenders_' + event_id).html(data).effect("highlight");
        }, "text");
    });

    $('.dateinput').datepicker({
        autoclose: true,
        format: dateformats[LOCALE],
        weekStart: 1,
    });

    $('.timeinput').timepicker({
        defaultTime: false,
        showMeridian: false,
    });

    $('[data-toggle="tooltip"]').tooltip();

    $('#ical-copy').click(function() {
        $('#ical-url').select();
        document.execCommand('copy');
    });

    var orig = $('form.disable-on-change').serialize();

    $('form.disable-on-change').bind('change keyup', function() {
        var disable = (orig != $(this).serialize());
        $('#complete').toggleClass('disabled', disable);
    });


});
