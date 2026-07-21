from src.utils.pagination import PaginatedResult


class TestPaginatedResult:

    def test_basic(self):
        r = PaginatedResult(items=[1, 2, 3], page=1, pages=3, total=3, per_page=1)
        assert r.items == [1, 2, 3]
        assert r.page == 1
        assert r.pages == 3
        assert r.total == 3
        assert r.per_page == 1

    def test_empty(self):
        r = PaginatedResult(items=[], page=1, pages=1, total=0, per_page=10)
        assert r.items == []
        assert r.total == 0
        assert r.pages == 1

    def test_single_page(self):
        r = PaginatedResult(items=['a', 'b'], page=1, pages=1, total=2, per_page=10)
        assert r.pages == 1
        assert len(r.items) == 2

    def test_many_pages(self):
        r = PaginatedResult(items=[], page=5, pages=10, total=100, per_page=10)
        assert r.page == 5
        assert r.pages == 10
        assert r.total == 100

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PaginatedResult)
