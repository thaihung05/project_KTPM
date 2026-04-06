function borrowBook(bookId) {
    fetch(`/api/borrow/${bookId}`, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status == 200) {
            Swal.fire({
                title: "Thành công!",
                text: data.message,
                icon: "success",
                showConfirmButton: false,
                timer: 800,
            }).then(() => {
                const qtyElement = document.getElementById(`qty-${bookId}`);
            if (qtyElement) {
                qtyElement.innerText = `Còn ${data.new_quantity} quyển`;
            }
            });
        } else {
            Swal.fire("Thông báo", data.message, "warning");        }
    })
    .catch(err => {
        console.error("Lỗi kết nối API:", err);
        Swal.fire({
                title: "Lỗi Hệ Thống!!",
                text: "Vui lòng đăng nhập trước khi mượn sách!!",
                icon: "error",
                showConfirmButton: true,
                showCancelButton: true,
        }).then((result) => {
            if (result.isConfirmed) {
                location.href = "/login";
            }
        })
    });
}

function addToCart(id, title) {
    fetch(`/api/cart`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            'id': id,
            'title': title
        })
    }).then(res => res.json())
    .then(data => {
        if (data.total_quantity !==undefined) {
            let counters = document.getElementsByClassName('cart-counter')
            for (let c of counters) {
                c.innerText = data.total_quantity
            }
            Swal.fire({
                title: "Đã thêm!!",
                text: `Sách "${title}" đã được thêm vào giỏ hàng của bạn!!`,
                icon: "success",
                showConfirmButton: false,
                timer: 1200
            })
        }
        else {Swal.fire("Lỗi!!", data.message, "error")}
    }).catch(err => {
        console.error("Lỗi kết nối API:", err);
        Swal.fire({
                title: "Lỗi Hệ Thống!!",
                text: "Vui lòng đăng nhập trước khi bỏ giỏ hàng!!",
                icon: "error",
                showConfirmButton: true,
                showCancelButton: true,
        }).then((result) => {
            if (result.isConfirmed) {
                location.href = "/login";
            }
        })
    });
}

function deleteCart(id) {
    Swal.fire({
        title: "Xóa khỏi giỏ?",
        text: "Bạn chắc chắn muốn xóa quyển này khỏi danh sách chờ?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, Delete it!",
        cancelButtonText: "Cancel"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/cart/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                let row = document.getElementById(`book-${id}`);
                if (row) row.remove();

                let counters = document.getElementsByClassName('cart-counter');
                for (let c of counters) {
                    c.innerText = data.total_quantity;
                }

                Swal.fire({
                    title: "Đã xóa!",
                    icon: "success",
                    timer: 800,
                    showConfirmButton: false
                });
            })
            .catch(err => Swal.fire("Lỗi", "Không xóa được!", "error"));
        }
    });
}

document.addEventListener('change', function(e) {
    if (e.target.classList.contains('book-sel')) {
        let selected = document.querySelectorAll('.book-sel:checked');
        if (selected.length > 5) {
            e.target.checked = false;
            Swal.fire("Quá giới hạn", "Mỗi lần chỉ được chọn tối đa 5 quyển sách!", "warning");
        }
        document.getElementById('selected-count').innerText = `Đã chọn: ${document.querySelectorAll('.book-sel:checked').length} quyển`;
    }
});

function borrowSelected() {
    let selectedCheckboxes = document.querySelectorAll('.book-sel:checked');
    let ids = Array.from(selectedCheckboxes).map(cb => cb.value);

    if (ids.length === 0) {
        return Swal.fire("Thông báo", "Bạn chưa chọn quyển nào để mượn hết!", "info");
    }

    fetch('/api/confirm-borrow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'book_ids': ids })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {
            Swal.fire({
                title: "Thành công!",
                text: data.message,
                icon: "success",
                showConfirmButton: false,
                timer: 800,
                timerProgressBar: true
            }).then(() => {
                location.href = "/cart";
            });
        } else {
            Swal.fire("Lỗi rồi", data.message, "error");
        }
    });
}

