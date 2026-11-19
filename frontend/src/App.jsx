
import "bootstrap/dist/css/bootstrap.min.css";
import ProductList from "./components/ProductList";

function App() {
  return (
    <>
      <nav className="navbar navbar-dark bg-dark px-4">
        <span className="navbar-brand fw-bold">
          Zan Phones
        </span>
      </nav>

      <ProductList />
    </>
  );
}

export default App;
