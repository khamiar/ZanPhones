
import { useEffect, useState } from "react";
import api from "../services/api";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("products/");
        setProducts(response.data);
      } catch (err) {
        setError("Failed to load products.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <p>Loading products...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div className="container py-4">
      <h2 className="mb-4">Our Products</h2>

      <div className="row">
        {products.map((product) => (
          <div className="col-md-4 mb-4" key={product.id}>
            <div className="card h-100">
              <img
                src={
                  product.images.find((image) => image.is_primary)?.image ||
                  product.images[0]?.image
                }
                className="card-img-top"
                alt={product.name}
                style={{ height: "220px", objectFit: "contain" }}
              />

              <div className="card-body">
                <h5>{product.name}</h5>

                <p className="text-muted">
                  {product.category_name}
                </p>

                <h6>
                  TZS {Number(product.price_tzs).toLocaleString()}
                </h6>

                <p>{product.description}</p>

                <button className="btn btn-primary">
                  View Product
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProductList;
