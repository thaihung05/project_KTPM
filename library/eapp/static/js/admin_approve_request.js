function approveReturn(detailId) {
    Swal.fire({
        title: 'Xác nhận duyệt sách?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Duyệt',
        cancelButtonText: 'Hủy',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/admin/approve-return/${detailId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    const fine = body.data && body.data.fine ? body.data.fine : 0;

                    Swal.fire(
                        'Thành công!',
                        `Duyệt trả sách thành công.${fine > 0 ? ' Phí phạt: ' + fine + 'đ.' : ''}`,
                        'success'
                    ).then(() => location.reload());
                } else {
                    Swal.fire('Thông báo', body.error || 'Có lỗi xảy ra.', 'warning');
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Lỗi', 'Không thể kết nối máy chủ.', 'error');
            });
        }
    });
}


function rejectReturn(detailId) {
    Swal.fire({
        title: 'Xác nhận từ chối duyệt sách?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Từ chối',
        cancelButtonText: 'Hủy',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/admin/reject-return/${detailId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    Swal.fire('Thành công!', body.message || 'Đã từ chối yêu cầu trả sách.', 'success')
                        .then(() => location.reload());
                } else {
                    Swal.fire('Thông báo', body.error || 'Có lỗi xảy ra.', 'warning');
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Lỗi', 'Không thể kết nối máy chủ.', 'error');
            });
        }
    });
}