$(document).ready(function () {
    $('.dropdown-item').on('click', function () {
        const filter = $(this).text();
        $('#btnSelect').html(filter);
        if (filter === "All") {
            $("#outboxList > li").each(function () {
                $(this).show();
            });
        } else {
            $("#outboxList > li").each(function () {
                if ($(this).children(".stat").data("stat").search(filter) > -1) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }
    });
});

function onFormSubmit(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("email1", document.getElementById("email1").value);
    formData.append("file1", document.getElementById("file1").files[0]);
    console.log(formData);
    jQuery.ajax({
        url: $("#urlsenddoc").val(),
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        method: 'POST',
        success: function (data) {
            infoAlert(
                "<strong>Success</strong>",
                `<p>${data}</p>`
            ).then(function () {
                location.reload();
            });
        }
    });
}

function readFile(docFile, docTitle, event) {
    event.preventDefault();
    const url = docFile + '?timestamp=' + new Date().getTime()
    $('#pdfPrev').attr("src", url);
    $('#pdfPrev').data("fileName", docTitle);
}

