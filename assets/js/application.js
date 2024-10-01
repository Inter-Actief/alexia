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

function setCookie(name, value, days) {
    var expires = '';
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '')  + expires + '; path=/';
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

function resetCommentPrompts() {
    $('.bartender_availability_comment').click(function () {
        let event_id = $(this).data('event-id');
        let comment = prompt('Enter a comment');

        if (comment == null || comment == '') {
            return;
        }

        if (comment.length > 100) {
            alert('Comment is too long. Maximum 100 characters allowed.');
            return;
        }

        const $this = $(this);

        $.post('/scheduling/ajax/bartender_availability/comment/', {
            event_id,
            comment
        }, function (data) {
            $this.replaceWith(data);
            resetCommentPrompts();
        }, "text");
    });
}

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

    resetCommentPrompts();

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

    $('[data-set-lang]').click(function() {
        var code = $(this).data('set-lang');
        $('form#set-lang-' + code).submit();
    });

    $('[data-print]').click(function(event) {
        event.preventDefault();
        var id = $(this).data('print').substr(1);
        document.getElementById(id).contentWindow.print();
    });
});
