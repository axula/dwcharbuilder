$('#save-character').click(function(e) {
    e.preventDefault;
    
});

$(document).ready(function() {
    $('.look-custom input:radio').click(function() {
        var parent = $(this).parent();
        $(parent).children('input:text').prop('required', true);
    });
    
    $("input:radio:first").prop("checked", true).trigger("click");
    
    $('[data-toggle="tooltip"]').tooltip({
        trigger : 'hover'
    })
});

$('#new-character').validate({
    //debug: true, 
    errorClass: 'error', 
    validClass: 'success', 
    highlight: function(element, errorClass, validClass) {
        $(element).addClass(errorClass).removeClass(validClass);
    }, 
    unhighlight: function(element, errorClass, validClass) {
        $(element).removeClass(errorClass).addClass(validClass);
    }, 
    showErrors: function(errorMap, errorList) {
        // Clean up any tooltips for valid elements
        $.each(this.validElements(), function (index, element) {
            var $element = $(element);
            $element.data("title", "") // Clear the title - there is no error associated anymore
                .removeClass("error")
                .tooltip("destroy");
        });
        // Create new tooltips for invalid elements
        $.each(errorList, function (index, error) {
            var $element = $(error.element);
            $element.tooltip("destroy") // Destroy any pre-existing tooltip so we can repopulate with new tooltip content
                .data("title", error.message)
                .addClass("error")
                .tooltip(); // Create a new tooltip based on the error messsage we just set in the title
        });
    }
});

$.validator.addClassRules("bond-group", {
    require_from_group: [1, ".bond-group"]
});

$('#new-character').on('keyup blur change', function () {
    if ($('#new-character').valid()) {
        $('#save-character').prop('disabled', false); 
    } else {
        $('#save-character').prop('disabled', 'disabled');
    }
});

$('#select-class').change(function() {
    var charclass = $(this).val();
    $('#class-content').load('/class/new', {
        charclass: charclass
    }, function(data) { });
    $('#save-character').prop('disabled', 'disabled');
});