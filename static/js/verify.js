$(document).ready(function () {

    const verifyUrl = $("#urlVerify").val();
    $("#docFile").on("change", function () {
        const f = this.files[0];
        $("#pdfPrev").attr("src", `${URL.createObjectURL(f)}#zoom=60`);
        $("#pdfPrev").removeClass("d-none");
    });
    $("#frmVerify").on("submit", function (e) {
        e.preventDefault();
        const fd = new FormData();
        fd.append("docFile", document.getElementById("docFile").files[0]);
        jQuery.ajax({
            url: verifyUrl,
            data: fd,
            contentType: false,
            processData: false,
            cache: false,
            method: 'POST',
            success: function (data) {
                fillModal(data.signs);
                $("#signatureModal").modal("show");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                errorAlert(
                   xhr.responseText
                );
            }
        });
    });
});

function fillModal(signs) {
    let lists = `<div class="treeview">
        <h6 class="pt-3 pl-3">Signatures</h6>
        <hr>
        <ul class="mb-1 pl-3 pb-2">`;
    for (const sign of signs) {
        let signItem = `
            <li><i class="fas fa-angle-right rotate"></i>
            <span><i class="fas fa-signature ic-w mx-1"></i>${sign.signer.common_name}</span>
            <ul class="nested">
                <li><i class="far fa-envelope-open ic-w mr-1"></i>${sign.signer.email_address[0]}</li>
                <li><i class="fas fa-angle-right rotate"></i>
                  <span><i class="fas fa-building ic-w mx-1"></i><span style="color: darkred">Issuer:</span> ${sign.cert_issuer.common_name}</span>
                  <ul class="nested">
                    <li><i class="far fa-flag ic-w mr-1"></i><span style="color: darkred">Country:</span> ${sign.cert_issuer.country_name}</li>
                    <li><i class="fas fa-city ic-w mr-1"></i><span style="color: darkred">City:</span> ${sign.cert_issuer.locality_name}</li>
                    <li><i class="fas fa-building ic-w mr-1"></i><span style="color: darkred">Organization:</span> ${sign.cert_issuer.organization_name}</li>
                  </ul>
                </li>
                <li><i class="far fa-clock ic-w mr-1"></i><span style="color: darkred">Date & Time:</span> ${sign.datetime}</li>
                <li><i class="fas fa-check mr-1"></i><span style="color: darkred">Document is Intact:</span> ${sign.intact}</li>
                <li><i class="fas fa-check mr-1"></i><span style="color: darkred">Signature is Trusted:</span> ${sign.trusted}</li>
            </ul>
            <hr/>
        `;
        lists += signItem;
    }
    lists += "</ul></div>";
    $("#signs-body").html(lists);
    $('.treeview').mdbTreeview();
}
