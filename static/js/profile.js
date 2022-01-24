$(document).ready(function () {
    $("#btnCleanPass").on('click', function () {
        $("#currentPass").val("");
        $("#newPass").val("");
        $("#newPassConf").val("");
    });

    $("#btnChangePass").on('click', function (event) {
        const curr = $("#currentPass").val();
        const newPass = $("#newPass").val();
        const newConf = $("#newPassConf").val();
        if (curr.length === 0 || newPass.length === 0 || newConf.length === 0) {
            alert("Please fill all 3 inputs to change the password.");
        } else {
            event.preventDefault();
            jQuery.ajax({
                url: $("#urlChangePass").val(),
                data: JSON.stringify({
                    currentPass: curr,
                    newPass: newPass,
                    newConf: newConf
                }),
                contentType: "application/json",
                processData: false,
                cache: false,
                method: 'POST',
                success: function (data) {
                    if (data.status === 200) {
                        infoAlert(
                            "<strong>Success</strong>",
                            `<p>${data.message}</p>`
                        );
                    } else {
                        errorAlert(
                            "<strong>Something went wrong!</strong>",
                            `</p>${data.message}</p>`
                        );
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.status);
                    alert(thrownError);
                }
            });
        }
    });

    $("#signHolder").on("click", function () {
        $("#signBrowse").on('change', function () {
            $(".dz-message").addClass("d-none");
            $("#signImage").removeClass("d-none");
            previewFile();
        }).click();
    });

    $("#uploadSign").on("click", function () {
        const signPass = $("#signPass").val();
        const signPassConf = $("#signPassConf").val();
        if (signPass.length === 0 || signPassConf.length === 0) {
            infoAlert(
                "<strong>Careful</strong>",
                `<p>Please fill both Signature Password and ins confirmation</p>`
            )
        } else {
            const formData = new FormData();
            formData.append("signPass", signPass);
            formData.append("signPassConf", signPassConf);
            formData.append("signImg", document.getElementById("signBrowse").files[0]);
            jQuery.ajax({
                url: $("#urlUploadSign").val(),
                data: formData,
                contentType: false,
                processData: false,
                cache: false,
                method: 'POST',
                success: function (data) {
                    if (data.status === 200) {
                        infoAlert(
                            "<strong>Success</strong>",
                            `<p>${data.message}</p>`
                        ).then(function (isConfirmed) {
                            location.reload();
                        });
                    } else {
                        errorAlert(
                            "<strong>Something went wrong!</strong>",
                            `</p>${data.message}</p>`
                        );
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.status);
                    alert(thrownError);
                }
            });
        }
    });
});

function previewFile() {
    const file = $("input[type=file]").get(0).files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function () {
            $("#signImage").attr("src", reader.result);
        }
        reader.readAsDataURL(file);
    }
}