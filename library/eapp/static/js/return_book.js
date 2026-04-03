function requestReturnBook(detailId) {
    Swal.fire({
        title: 'Xác nhận trả sách?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Đồng ý',
        cancelButtonText: 'Hủy',
        reverseButtons: true
    })
    .then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/return-request/${detailId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    Swal.fire("Thành công!", body.message, "success")
                        .then(() => location.reload());
                } else {
                    Swal.fire("Thông báo", body.error || "Có lỗi xảy ra.", "warning");
                }
            })
            .catch(err => {
                Swal.fire("Lỗi", "Không thể kết nối máy chủ.", "error");
            });
        }
    })
}