from typing import List, Optional
from product_analysis.application.port.product_repository_port import ProductRepositoryPort
from product_analysis.domain.entity.product import Product, Platform


class ProductUseCase:

    def __init__(self, product_repo: ProductRepositoryPort):
        self.product_repo = product_repo

    def create_product(self, product: Product) -> Product:
        exists = self.product_repo.find_by_composite_key(
            product.source, product.source_product_id
        )

        if exists:
            raise Exception("이미 존재하는 상품입니다.")

        return self.product_repo.save(product)

    def get_product_by_composite_key(self, source: Platform, source_product_id: str) -> Optional[Product]:
        return self.product_repo.find_by_composite_key(source, source_product_id)

    def get_all_products(self, limit: int = 10) -> List[Product]:
        return self.product_repo.find_all(limit)

    def search_products(self, source: Platform, keyword: str) -> List[Product]:
        return self.product_repo.find_by_title_like(source, keyword)

    def update_product(self, product: Product) -> Product:
        exists = self.product_repo.find_by_composite_key(
            product.source, product.source_product_id
        )

        if not exists:
            raise ValueError("업데이트할 상품이 존재하지 않습니다.")

        return self.product_repo.update(product)

    def delete_product(self, source: Platform, source_product_id: str) -> bool:
        return self.product_repo.delete(source, source_product_id)
