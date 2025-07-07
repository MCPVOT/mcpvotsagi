import { getProducts } from '@/lib/products-api';

type ProductListingPageProps = Record<string, never>;

export default async function ProductListingPage({}: ProductListingPageProps) {
  // Real API call to get products
  const products = await getProducts();

  // Simple product list display (no more mock table components)
  return (
    <div className="space-y-4 p-6">
      <h2 className="text-2xl font-bold">Products</h2>
      <div className="grid gap-4">
        {products.map((product) => (
          <div key={product.id} className="border rounded-lg p-4 bg-white shadow">
            <h3 className="font-semibold text-lg">{product.name}</h3>
            <p className="text-gray-600 mb-2">{product.description}</p>
            <div className="flex justify-between items-center">
              <p className="text-lg font-bold text-green-600">${product.price}</p>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                {product.category}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
