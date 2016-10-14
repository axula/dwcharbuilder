/* Admin Pages */

$('#new').on('shown.bs.modal', function () {
  $('#myInput').focus()
})

$(document).ready( function() {
    function setNavbarActive() {
        var page_name = document.getElementById("page").className;
        document.getElementById("link-" + page_name).className = "active";
    }
    $('.equipment-list').height( $(window).height() - 260 );
    
    $('#equipment ul').each(function(index, element) {
        if( $(element).children('li').length > 1 ) {
            $(element).children('.empty').hide();
        }
    });
});

$(window).resize( function() {
    $('.equipment-list').height( $(window).height() - 260 );
});

// Upload Image Preview
$('#image_file').change( function () {
    var reader = new FileReader();
    
    reader.onload = function (e) {
        // get loaded data and render thumbnail
        $('#image-preview img').attr('src', e.target.result);
    };
    
    // read the image file as a data URL
    reader.readAsDataURL(this.files[0]);
});

/* Equipment */

$('.equipmentNav').click( function(e) {
    e.preventDefault;
    var type = $(this).data('type');
    $('.equipmentNav').removeClass('active');
    $(this).addClass('active');
    $('.equipment-list').find('a').each(function(){
        if( $(this).data('type') === type ) {
            $(this).parent().removeClass('hide');
        } else {
            $(this).parent().addClass('hide');
        }
    });
});

$(document).on('keyup', '#search-items', function() {
    var search = $(this).val().toLowerCase();
    $('.equipment-list>li').each(function () {
        var text = $(this).text().toLowerCase();
        ( text.indexOf(search) != -1) ? $(this).show() : $(this).hide();
    });
});

$('.equipment-list li a').click( function() {
    $('.equipment-list li').removeClass('active');
    $(this).parent().addClass('active');
});

function addToBackpack(id, name, tags, type, description) {
    $('#backpack-' + type).append(
        '<li data-id="' + id + '" data-description="' + description + '"><b>' + name + '</b> ' + tags + '<a class="pull-right" href="#"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a></li>' );
    if( $('#backpack-' + type + ' li').length > 1 ) {
        $('#backpack-' + type + ' .empty').hide();
    }
}

function removeGear(id) {
    var answer = confirm("Are you sure you wish to remove this item?")
    if (answer) {
        $.ajax({
            url: '/equipment/remove',
            data: JSON.stringify({ id : id }, null, '\t'), 
            contentType: "application/json; charset=utf-8", 
            type: 'POST',
            success: function(data) {
                removeFromBackpack( id );
                $('#current-load').text(data.load);
                $('#armor-bonus').text(data.armor);
            },
            error: function(error) {
                console.log("Error!");
            }
        });
    }
}

function removeFromBackpack(id) {
    var removed = $('#equipment ul').find("[data-id='" + id + "']");
    var parent = $(removed).parent();
    $(removed).remove();
    if( $(parent).children('li').length === 1 ) {
        $(parent).children('.empty').show();
    }
}

function addItemToInventory(is_buying) {
    var data = { name : $('.equipment-list li.active a').data('name'), 
                 source : $('.equipment-list li.active a').data('source'), 
                 type : $('.equipment-list li.active a').data('type'), 
                 is_buying : is_buying, id : $CHARACTERID }
    $.ajax({
        url: '/equipment/add',
        data: JSON.stringify(data, null, '\t'), 
        contentType: "application/json; charset=utf-8", 
        type: 'POST',
        success: function(data) {
            addToBackpack(data.id, data.name, data.tags, data.type, data.description);
            $('#current-load').text(data.load);
        },
        error: function(error) {
            console.log("Error!");
        }
    });
}

$('#add-equipment').click( function() {
    addItemToInventory(false);
});

$('#buy-equipment').click( function() {
    addItemToInventory(true);
});