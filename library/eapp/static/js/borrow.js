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
            Swal.fire("Thành công!", data.message, "success");
            const qtyElement = document.getElementById(`qty-${bookId}`);
            if (qtyElement) {
                qtyElement.innerText = `Còn ${data.new_quantity} cuốn`;
            }
        } else {
            Swal.fire("Thông báo", data.message, "warning");        }
    })
    .catch(err => {
        console.error("Lỗi kết nối API:", err);
        Swal.fire("Lỗi", "Không thể kết nối máy chủ", "error");
    });
}
