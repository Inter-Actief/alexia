var LOCALE = $('html').attr('lang') || 'en';
var csrftoken = getCookie('csrftoken');

var THEME_STORAGE_KEY = 'alexia-theme';
var THEME_ICONS = {
    light: 'bi-sun-fill',
    dark: 'bi-moon-stars-fill',
    auto: 'bi-circle-half',
};
var prefersDarkQuery = window.matchMedia('(prefers-color-scheme: dark)');

function getStoredTheme() {
    var theme = localStorage.getItem(THEME_STORAGE_KEY);
    return (theme === 'light' || theme === 'dark') ? theme : 'auto';
}

function resolveTheme(theme) {
    if (theme === 'auto') {
        return prefersDarkQuery.matches ? 'dark' : 'light';
    }
    return theme;
}

function applyTheme(theme) {
    var resolved = resolveTheme(theme);
    document.documentElement.setAttribute('data-bs-theme', resolved);
    document.documentElement.setAttribute('data-color-scheme', resolved);
}

function updateThemeMenu(theme) {
    $('#theme-icon').attr('class', 'bi ' + THEME_ICONS[theme]);
    $('[data-theme-value]').each(function () {
        var active = $(this).data('theme-value') === theme;
        $(this).toggleClass('active', active);
        $(this).find('.bi-check2').toggleClass('d-none', !active);
    });
}

function setTheme(theme) {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    applyTheme(theme);
    updateThemeMenu(theme);
}

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
            // Update both the desktop table row and the mobile card. The
            // IVA status is derived from the assigned bartenders, so refresh
            // it alongside the names.
            $('#assigned_bartenders_' + event_id).html(data.bartenders);
            $('#assigned_bartenders_mobile_' + event_id).html(data.bartenders);
            $('#iva_' + event_id).html(data.iva);
            $('#iva_mobile_' + event_id).html(data.iva_mobile);
            $('.bartender_availability_comment[data-event-id="' + event_id + '"]').css('visibility', 'visible');
        }, "json");
    });

    resetCommentPrompts();

    applyTheme(getStoredTheme());
    updateThemeMenu(getStoredTheme());

    $('[data-theme-value]').click(function () {
        setTheme($(this).data('theme-value'));
    });

    prefersDarkQuery.addEventListener('change', function () {
        if (getStoredTheme() === 'auto') {
            applyTheme('auto');
        }
    });

    $('[data-bs-toggle="tooltip"]').each(function () {
        new bootstrap.Tooltip(this);
    });

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
