$(function() {
    var orig = $('form').serialize();

    $('form').bind('change keyup', function() {
        var disable = (orig != $(this).serialize());
        $('#complete').toggleClass('disabled', disable);
    });
});
