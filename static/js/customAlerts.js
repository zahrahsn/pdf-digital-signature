function infoAlert(title, body) {
    return Swal.fire({
        title: title,
        icon: 'info',
        html: body,
        showCloseButton: false,
        focusConfirm: false,
        confirmButtonText:
            '<i class="fa fa-thumbs-up"></i> Great!',
        confirmButtonAriaLabel: 'OK',
    });
}

function errorAlert(title, body) {
    return Swal.fire({
        title: title,
        icon: 'error',
        html: body,
        showCloseButton: false,
        focusConfirm: false,
        confirmButtonText:
            '<i class="fa fa-thumbs-down"></i> Oops!',
        confirmButtonAriaLabel: 'OK',
    });
}

function confirmAlert(title, body) {
    return Swal.fire({
        title: title,
        icon: 'warning',
        html: body,
        showCloseButton: false,
        showCancelButton: true,
        focusConfirm: false,
        confirmButtonText:
            '<i class="fa fa-thumbs-up"></i> Yes',
        cancelButtonText:
            '<i class="fa fa-thumbs-down"></i> No',
    });
}