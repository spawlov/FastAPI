from typing import Any, Optional
from fastapi import FastAPI, HTTPException

sample_product_1: dict[str, Any] = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99,
}

sample_product_2: dict[str, Any] = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99,
}

sample_product_3: dict[str, Any] = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99,
}

sample_product_4: dict[str, Any] = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99,
}

sample_product_5: dict[str, Any] = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99,
}

sample_products: list[dict[str, Any]] = [
    sample_product_1,
    sample_product_2,
    sample_product_3,
    sample_product_4,
    sample_product_5,
]

app = FastAPI()


@app.get("/product/{product_id}")
async def get_product_by_id(product_id: int) -> dict[str, Any]:
    product: dict[str, Any] | None = next(
        (item for item in sample_products if item["product_id"] == product_id), None
    )
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/search")
async def search_product(
    keyword: str,
    category: Optional[str] = None,
    limit: Optional[int] = 10,
) -> list[dict[str, Any]]:

    results: list[dict[str, Any]] = [
        product
        for product in sample_products
        if keyword.lower() in product["name"].lower()
    ]

    if category:
        results = [
            product
            for product in results
            if product["category"].lower() == category.lower()
        ]

    if results:
        return results[:limit]
    raise HTTPException(status_code=404, detail="Product(s) not found")
