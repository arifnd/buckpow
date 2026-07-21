from sqlalchemy.orm import Query

from src.utils.pagination import PaginatedResult


class FilterBuilder:
    def __init__(self, model, query: Query):
        self.model = model
        self.query = query

    def eq(self, **kwargs) -> "FilterBuilder":
        for attr, value in kwargs.items():
            if value is not None:
                col = getattr(self.model, attr)
                self.query = self.query.filter(col == value)
        return self

    def date_range(self, col_name: str, start=None, end=None) -> "FilterBuilder":
        col = getattr(self.model, col_name)
        if start is not None:
            self.query = self.query.filter(col >= start)
        if end is not None:
            self.query = self.query.filter(col <= end)
        return self

    def is_null(self, col_name: str, is_null: bool = True) -> "FilterBuilder":
        col = getattr(self.model, col_name)
        if is_null:
            self.query = self.query.filter(col.is_(None))
        else:
            self.query = self.query.filter(col.isnot(None))
        return self

    def order(self, col_name: str, desc: bool = True) -> "FilterBuilder":
        col = getattr(self.model, col_name)
        if desc:
            self.query = self.query.order_by(col.desc())
        else:
            self.query = self.query.order_by(col)
        return self

    def limit(self, n: int) -> "FilterBuilder":
        self.query = self.query.limit(n)
        return self

    def paginate(self, page: int, per_page: int = 10) -> PaginatedResult:
        offset = (page - 1) * per_page
        total = self.query.count()
        items = self.query.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)
