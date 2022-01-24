let signCounter = 0;

$(document).ready(function () {
    const pdfUrl = $("#pdfFile").val();
    renderPDF(
        pdfUrl,
        document.getElementById("documentRender"),
        {scale: 1.55}
    );

    $("#addSign").on("click", function () {
        signCounter += 1;
        $("#deleteInstruction").removeClass("invisible");
        const url = $("#signUrl").val();
        const signature = `
            <div class="digital-signature" id="sign-${signCounter}" ondblclick="deleteSign(event)">
                   <img src="${url}" class="img-fluid signature-item" alt="">
            </div>`;
        $("#documentRender").prepend(signature);
        let scrollTop = $(document).scrollTop();
        let newSign = $(`#sign-${signCounter}`);
        let drg = newSign.draggable();
        drg.simulate(
            "drag",
            {dx: 0, dy: scrollTop}
        );
    });

    $("#applySign").on("click", async function (event) {
        event.preventDefault();
        let result = appendToPages();
        let signPass = await getSignPass();
        const data = {
            'pdfFile': $("#pdfFilePath").val(),
            'fileName': $("#pdfFileTitle").val(),
            'signPass': signPass,
            'signs': result
        }
        // console.log(JSON.stringify(result));
        jQuery.ajax({
            url: $("#applySign").data("url"),
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json",
            processData: false,
            cache: false,
            method: 'POST',
            success: function (data) {
                infoAlert(
                    "<strong>Success</strong>",
                    `<p>${data.message}</p>`
                ).then(function (isConfirmed) {
                    window.location.replace("/inbox");
                });
            },
            error: function (xhr, ajaxOptions, thrownError) {
                errorAlert(
                    "<strong>Something went wrong!</strong>",
                    `</p>${xhr.responseText}</p>`
                );
            }
        });
    });
});

function deleteSign(event) {
    let elm = event.target;
    if (elm.classList.contains("digital-signature--remove")) {
        elm.remove();
    } else {
        elm.parentNode.remove();
    }
    signCounter -= 1;
    if (signCounter < 1) {
        $("#deleteInstruction").addClass("invisible");
    }
}

function appendToPages() {
    let result = []
    const pageContainers = $(".pageContainer");
    const signatures = $(".digital-signature");
    for (let i = 1; i <= pageContainers.length; i++) {
        let page = $(`#page-${i}`);
        let pageTop = page.offset().top;
        let pageBottom = pageTop + page.height();
        // console.log(`Page-${i} top= ${pageTop}`);
        // console.log(`Page-${i} bottom= ${pageBottom}`);
        for (let j = 1; j <= signatures.length; j++) {
            let signature = $(`#sign-${j}`)
            let signatureTop = signature.offset().top;
            let signatureBottom = signatureTop + signature.height();
            // console.log(`Signature-${j} top= ${signatureTop}`);
            // console.log(`Signature-${j} bottom= ${signatureBottom}`);
            if ((signatureTop > pageTop) && (signatureBottom < pageBottom)) {
                signature.appendTo(page);
                result.push(
                    {
                        'page': $(page).attr("id"),
                        'page_width': page.width(),
                        'page_height': page.height(),
                        'sign_top': signature.position().top - page.position().top,
                        'sign_left': signature.position().left - page.position().left,
                        'sign_width': signature.width(),
                        'sign_height': signature.height()
                    }
                )
            }
        }
    }
    return result;
}

async function getSignPass() {
    const {value: password} = await Swal.fire({
        title: 'Enter your signature password',
        input: 'password',
        inputLabel: 'Password',
        inputPlaceholder: 'Enter your password',
        inputAttributes: {
            autocapitalize: 'off',
            autocorrect: 'off'
        }
    });
    if (password) {
        return password;
    }
}