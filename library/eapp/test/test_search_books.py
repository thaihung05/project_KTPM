import pytest
from eapp.dao import load_books, count_books
from eapp.test.test_base import test_app, sample_books, test_session, test_client

def test_all(sample_books):
    books = load_books(page_size=50)
    assert len(books) == len(sample_books)

def test_kw(sample_books):
    books = load_books(kw='Python', search_by='title', page_size=50)
    assert len(books) == 3
    assert all('Python' in b.title for b in books)

    books = load_books(kw='python', search_by='title', page_size=50)
    assert len(books) == 3

    books = load_books(kw='Ruby', search_by='title', page_size=50)
    assert len(books) == 0

    books = load_books(kw='Trần Văn A', search_by='author', page_size=50)
    assert len(books) == 2
    assert all('Trần Văn A' in b.author for b in books)

    books = load_books(kw='Tô Hoài', search_by='author', page_size=50)
    assert len(books) == 1

    books = load_books(kw='XYZ', search_by='author', page_size=50)
    assert len(books) == 0

    books = load_books(kw='', search_by='title', page_size=50)
    assert len(books) == 8

    books = load_books(kw='Python', search_by=None, page_size=50)
    assert len(books) == 8

    books = load_books(kw='Python', search_by='description', page_size=50)
    assert len(books) == 8

def test_cate_id(sample_books):
    books = load_books(cate_id=1, page_size=50)
    assert len(books) == 4
    assert all(b.category_id == 1 for b in books)

    books = load_books(cate_id=2, page_size=50)
    assert len(books) == 4
    assert all(b.category_id == 2 for b in books)

    books = load_books(cate_id=999, page_size=50)
    assert len(books) == 0

    books = load_books(cate_id=-1, page_size=50)
    assert len(books) == 0

    books = load_books(cate_id='1', page_size=50)
    assert len(books) == 4

    books = load_books(cate_id=None, page_size=50)
    assert len(books) == 8

    books = load_books(cate_id=0, page_size=50)
    assert len(books) == 8


def test_paging(sample_books, test_app):
    books = load_books(page=1, page_size=3)
    assert len(books) == 3

    books = load_books(page=2, page_size=3)
    assert len(books) == 3

    books = load_books(page=3, page_size=3)
    assert len(books) == 2

    books = load_books(page=4, page_size=3)
    assert len(books) == 0

    books = load_books(page=0, page_size=3)
    assert len(books) == 8

    books = load_books(page=1, page_size=None)
    assert len(books) == min(len(sample_books), test_app.config["PAGE_SIZE"])


def test_combo(sample_books):
    books = load_books(kw='Python', search_by='title', cate_id=1, page_size=50)
    assert len(books) == 3
    assert all('Python' in b.title for b in books)
    assert all(b.category_id == 1 for b in books)

    books = load_books(kw='Python', search_by='title', cate_id=2, page_size=50)
    assert len(books) == 0

    books = load_books(kw='', search_by='title', cate_id=1, page_size=50)
    assert len(books) == 4  # kw rỗng → chỉ lọc cate

    books = load_books(kw='Tô Hoài', search_by='author', cate_id=2, page_size=50)
    assert len(books) == 1

    books = load_books(kw='Python', search_by='title', cate_id=1, page=1, page_size=1)
    assert len(books) == 1

    books = load_books(kw='Python', search_by='title', cate_id=1, page=3, page_size=1)
    assert len(books) == 1

    books = load_books(kw='Python', search_by='title', cate_id=1, page=4, page_size=1)
    assert len(books) == 0

    books = load_books(kw='Python', search_by='title', cate_id=999, page_size=50)
    assert len(books) == 0


def test_count(sample_books):
    assert count_books() == 8

    assert count_books(kw='Python', search_by='title') == 3
    assert count_books(kw='Ruby', search_by='title') == 0

    assert count_books(kw='Tô Hoài', search_by='author') == 1
    assert count_books(kw='Trần Văn A', search_by='author') == 2

    assert count_books(kw='Python', search_by=None) == 8

    assert count_books(cate_id=1) == 4
    assert count_books(cate_id=2) == 4
    assert count_books(cate_id=999) == 0

    assert count_books(kw='Python', search_by='title', cate_id=1) == 3
    assert count_books(kw='Python', search_by='title', cate_id=2) == 0
    assert count_books(kw='Tô Hoài', search_by='author', cate_id=2) == 1


@pytest.mark.parametrize('kw', ['C++', 'C#', 'Java (Core)', '   Python   ', 'python123!@#'])
def test_special_chars(sample_books, kw):
    try:
        books = load_books(kw=kw, search_by='title', page_size=50)
        assert books is not None
        assert isinstance(books, list)
    except Exception as e:
        pytest.fail(f"load_books() không được raise exception với kw='{kw}', lỗi: {e}")


@pytest.mark.timeout(2)
def test_performance(sample_books):
    for page in range(1, 6):
        load_books(kw='Python', search_by='title', cate_id=1, page=page, page_size=2)
    load_books(page_size=50)
    load_books(kw='Tô Hoài', search_by='author', page_size=50)
    load_books(cate_id=2, page_size=50)


@pytest.mark.parametrize('kw, should_warn', [
    ('a', True),
    ('py', False),
    ('Python', False),
])
def test_kw_min_length(test_client, sample_books, kw, should_warn):
    res = test_client.get(f'/books?kw={kw}&search_by=title')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    msg = 'Vui lòng nhập từ 2 ký tự'
    if should_warn:
        assert msg in html
    else:
        assert msg not in html


def test_route(test_client, sample_books):
    res = test_client.get('/books')
    assert res.status_code == 200

    res = test_client.get('/books?kw=Python&search_by=title')
    assert res.status_code == 200
    assert 'Python' in res.data.decode('utf-8')
    assert 'Không tìm thấy' not in res.data.decode('utf-8')

    res = test_client.get('/books?kw=Ruby&search_by=title')
    assert res.status_code == 200
    assert 'Không tìm thấy' in res.data.decode('utf-8')

    res = test_client.get('/books?kw=Tô+Hoài&search_by=author')
    assert res.status_code == 200
    assert 'Tô Hoài' in res.data.decode('utf-8')

    res = test_client.get('/books?category_id=1')
    assert res.status_code == 200

    res1 = test_client.get('/books?page=1')
    res2 = test_client.get('/books?page=2')
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.data != res2.data
