from dataclasses import dataclass


@dataclass
class PaginatedResult:
    items: list
    page: int
    pages: int
    total: int
    per_page: int
