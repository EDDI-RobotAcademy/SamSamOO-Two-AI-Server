class Product:
    def __init__(self, product_id, name, price, mall, image, link, catalog_id):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.mall = mall
        self.image = image
        self.link = link
        self.catalog_id = catalog_id

    def to_dict(self):
        return {
            "productId": self.product_id,
            "name": self.name,
            "price": self.price,
            "mall": self.mall,
            "image": self.image,
            "link": self.link,
            "catalogId": self.catalog_id
        }
