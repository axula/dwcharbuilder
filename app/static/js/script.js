/* Admin Pages */

$('#new').on('shown.bs.modal', function () {
  $('#myInput').focus()
})

function setNavbarActive() {
	var page_name = document.getElementById("page").className;
	document.getElementById("link-" + page_name).className = "active";
}

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