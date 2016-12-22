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

$(function () {

    $('.bartender_availability').change(function () {
        var event_id = $(this).data('event-id');

        $.post('/scheduling/ajax/bartender_availability/', {
            event_id: event_id,
            availability_id: $(this).val(),
            csrfmiddlewaretoken: getCookie('csrftoken')
        }, function (data) {
            $('#assigned_bartenders_' + event_id).html(data).effect("highlight");
        }, "text");
    });

    $('.dateinput').datepicker({
        autoclose: true,
        format: gettext('yyyy-mm-dd'),
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
