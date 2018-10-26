$("#fileUpload").submit(function() {
  let files = $('#'+this.id+' input[type="file"]').val();
  if (files == '') {
    $("#upload-feedback").html("Please select at least one file to upload.");
    return false;
  }
});
