class DanawaProduct:
    def __init__(self, product_id, name, price, mall, image, link, category_id=None):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.mall = mall
        self.image = image
        self.link = link
        self.category_id = category_id

    def to_dict(self):
        return {
            "productId": self.product_id,
            "name": self.name,
            "price": self.price,
            "mall": self.mall,
            "image": self.image,
            "link": self.link,
            "categoryId": self.category_id,
        }
