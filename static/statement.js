function previewFile() {
    var fileInput = document.getElementById('file');
    var preview = document.getElementById('preview');
    var fileIcon = document.getElementById('file-icon');
    var fileName = fileInput.files[0].name;
    var ext = fileName.split('.').pop().toLowerCase();
    var allowedExts = ['csv', 'xls', 'xlsx'];
    if (allowedExts.indexOf(ext) === -1) {
        preview.innerHTML = 'Por favor, selecione um arquivo Excel ou CSV.';
        fileIcon.src = '';
    } else if (allowedExts.indexOf(ext) === 1 || allowedExts.indexOf(ext) === 2) {
        preview.innerHTML = fileName;
        fileIcon.src = fileIcon.src = "../static/images/xls_icon.png";
    } else {
        preview.innerHTML = fileName;
        fileIcon.src = fileIcon.src = "../static/images/csv_icon.png";
    }
}