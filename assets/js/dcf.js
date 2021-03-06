(function($) {

    $.fn.dynamicFormset = function(opts) {
        var options = $.extend({}, $.fn.dynamicFormset.defaults, opts);

        var $this = $(this);
        var $parent = $this.parent();
        var $totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS");
        var $template = $this.last().clone();
        var nextIndex = parseInt($totalForms.val());

        var updateIndex = function(element, prefix, index) {
            var search = prefix + '-__prefix__';
            var replace = prefix + '-' + index;
            if (element.id) {
                element.id = element.id.replace(search, replace);
            }
            if (element.name) {
                element.name = element.name.replace(search, replace);
            }
        };

        var colspan = $('thead tr th', $parent.parent()).length + 2;
        $parent.append('<tr class="dynamic-form-add" ><td colspan="' + colspan + '"><a href="#"><span class="glyphicon glyphicon-plus"></span></a></td></tr>');
        var $addButton = $('tr:last a', $parent);

        $addButton.click(function(event) {
            event.preventDefault();

            var $template = $('#' + options.prefix + '-empty');
            var $row = $template.clone();
            $row.attr('id', options.prefix + '-' + nextIndex);
            $row.removeClass('dynamic-form-empty');
            $row.find("*").each(function() {
                updateIndex(this, options.prefix, nextIndex);
            });
            $('.dynamic-form-add', $parent).before($row);

            nextIndex++;
            $totalForms.val(nextIndex);
        });
    };

    $.fn.dynamicFormset.defaults = {
        prefix: '',
        addButtonSelector: '',
    };

})(jQuery);

$(function() {
    $('.dynamic-formset').each(function() {
        var prefix = $(this).data('prefix');
        $('tbody tr', this).dynamicFormset({
            prefix: prefix,
        });
    });

    var orig = $('form.disable-on-change').serialize();

    $('form.disable-on-change').bind('change keyup', function() {
        var disable = (orig != $(this).serialize());
        $('#complete').toggleClass('disabled', disable);
    });

    var FLOWMETER_URL = 'https://flowmeterpi.ia.utwente.nl/data.php';
    var timeout;

    $(document).on('keypress', '.flowmeter', function() {
        $('#flowmeterWarning').slideUp();

        if (timeout) {
            clearTimeout(timeout);
        }

        var $input = $(this);

        timeout = setTimeout(function() {
            $.get(FLOWMETER_URL, function(data) {
                var user = parseFloat($input.val().replace(',', '.'));
                var live = parseFloat(data[location_name].reading);
                var diff = Math.abs(user - live);
                
                if (diff > 1.0) {
                    $('#flowmeterWarning').html('<strong>Waarschuwing:</strong> Ingevoerde flowmeterstand (' + user.toFixed(1) + ') wijkt af van live stand (' + live.toFixed(1) + ').');
                    $('#flowmeterWarning').slideDown();
                }
            });
        }, 1000);
    });
});
