$(document).ready(function () {
    $('.dropdown-item').on('click', function () {
        const filter = $(this).text();
        $('#btnSelect').html(filter);
        if (filter === "All") {
            $("#messagesList > li").each(function () {
                $(this).show();
            });
        } else {
            $("#messagesList > li").each(function () {
                if ($(this).children(".stat").data("stat").search(filter) > -1) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }
    });
    $("#pdfPrev").on('load', function () {
        const srcVal = $("#pdfPrev").attr("src");
        const fileName = $('#pdfPrev').data("fileName")
        $("#pdfData").val(srcVal);
        $("#pdfFile").val(fileName);
        if (srcVal !== "") {
            $("#docForm").removeClass("d-none");
        } else {
            $("#docForm").addClass("d-none");
        }
    });
    $("#reject").on('click', function () {
        confirmAlert(
            "<strong>Reject the signing request</strong>",
            `<p>Do you really want to reject this request?</p>`
        ).then(function (result) {
            if (result.isConfirmed) {
                const url = $("#urlReject").val();
                const pdfFile = $("#pdfFile").val();
                jQuery.ajax({
                    url: url,
                    data: JSON.stringify({fileName: pdfFile}),
                    contentType: "application/json",
                    processData: false,
                    cache: false,
                    method: 'POST',
                    success: function (data) {
                        infoAlert(
                            "<strong>Success</strong>",
                            `<p>${data}</p>`
                        );
                        location.reload();
                    }
                });
            }
        });
    });
});