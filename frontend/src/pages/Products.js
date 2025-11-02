import React, { useEffect, useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { productService } from '../api/services';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Search, Package } from 'lucide-react';

const ProductForm = ({ product, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState(
    product || {
      name: '',
      sku: '',
      description: '',
      category: '',
      brand: '',
      unit: 'piece',
      pricing: {
        purchasePrice: 0,
        sellingPrice: 0,
        mrp: 0,
        discount: 0,
        taxRate: 18,
      },
      stock: {
        quantity: 0,
        reorderPoint: 0,
        warehouse: 'Main',
      },
    }
  );
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (product?.id) {
        await productService.updateProduct(product.id, formData);
        toast.success('Product updated successfully');
      } else {
        await productService.createProduct(formData);
        toast.success('Product created successfully');
      }
      onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="product-form">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="name">Product Name *</Label>
          <Input
            id="name"
            data-testid="product-name-input"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="sku">SKU *</Label>
          <Input
            id="sku"
            data-testid="product-sku-input"
            value={formData.sku}
            onChange={(e) =>
              setFormData({ ...formData, sku: e.target.value.toUpperCase() })
            }
            required
            disabled={!!product?.id}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="category">Category *</Label>
          <Input
            id="category"
            data-testid="product-category-input"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="brand">Brand</Label>
          <Input
            id="brand"
            data-testid="product-brand-input"
            value={formData.brand}
            onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
          />
        </div>
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <textarea
          id="description"
          data-testid="product-description-input"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Unit</Label>
          <Select
            value={formData.unit}
            onValueChange={(value) => setFormData({ ...formData, unit: value })}
          >
            <SelectTrigger data-testid="product-unit-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="piece">Piece</SelectItem>
              <SelectItem value="kg">Kilogram</SelectItem>
              <SelectItem value="liter">Liter</SelectItem>
              <SelectItem value="meter">Meter</SelectItem>
              <SelectItem value="box">Box</SelectItem>
              <SelectItem value="dozen">Dozen</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="font-semibold mb-3">Pricing</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="purchasePrice">Purchase Price *</Label>
            <Input
              id="purchasePrice"
              type="number"
              data-testid="product-purchase-price-input"
              step="0.01"
              value={formData.pricing.purchasePrice}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  pricing: { ...formData.pricing, purchasePrice: parseFloat(e.target.value) },
                })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="sellingPrice">Selling Price *</Label>
            <Input
              id="sellingPrice"
              type="number"
              data-testid="product-selling-price-input"
              step="0.01"
              value={formData.pricing.sellingPrice}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  pricing: { ...formData.pricing, sellingPrice: parseFloat(e.target.value) },
                })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="mrp">MRP *</Label>
            <Input
              id="mrp"
              type="number"
              data-testid="product-mrp-input"
              step="0.01"
              value={formData.pricing.mrp}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  pricing: { ...formData.pricing, mrp: parseFloat(e.target.value) },
                })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="discount">Discount (%)</Label>
            <Input
              id="discount"
              type="number"
              data-testid="product-discount-input"
              step="0.01"
              value={formData.pricing.discount}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  pricing: { ...formData.pricing, discount: parseFloat(e.target.value) },
                })
              }
            />
          </div>
          <div>
            <Label htmlFor="taxRate">Tax Rate (%)</Label>
            <Input
              id="taxRate"
              type="number"
              data-testid="product-tax-rate-input"
              step="0.01"
              value={formData.pricing.taxRate}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  pricing: { ...formData.pricing, taxRate: parseFloat(e.target.value) },
                })
              }
            />
          </div>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="font-semibold mb-3">Stock</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="quantity">Quantity *</Label>
            <Input
              id="quantity"
              type="number"
              data-testid="product-quantity-input"
              value={formData.stock.quantity}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  stock: { ...formData.stock, quantity: parseFloat(e.target.value) },
                })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="reorderPoint">Reorder Point</Label>
            <Input
              id="reorderPoint"
              type="number"
              data-testid="product-reorder-point-input"
              value={formData.stock.reorderPoint}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  stock: { ...formData.stock, reorderPoint: parseFloat(e.target.value) },
                })
              }
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" data-testid="product-submit-btn" disabled={loading}>
          {loading ? 'Saving...' : product?.id ? 'Update Product' : 'Create Product'}
        </Button>
      </div>
    </form>
  );
};

export const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, [search]);

  const fetchProducts = async () => {
    try {
      const data = await productService.getProducts({ search, limit: 100 });
      setProducts(data);
    } catch (error) {
      toast.error('Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productService.deleteProduct(id);
        toast.success('Product deleted successfully');
        fetchProducts();
      } catch (error) {
        toast.error('Failed to delete product');
      }
    }
  };

  const handleSuccess = () => {
    setDialogOpen(false);
    setSelectedProduct(null);
    fetchProducts();
  };

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="products-page">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Products</h2>
            <p className="text-gray-600 mt-1">Manage your inventory</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button
                data-testid="add-product-btn"
                onClick={() => {
                  setSelectedProduct(null);
                  setDialogOpen(true);
                }}
              >
                <Plus size={20} className="mr-2" />
                Add Product
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {selectedProduct ? 'Edit Product' : 'Add New Product'}
                </DialogTitle>
              </DialogHeader>
              <ProductForm
                product={selectedProduct}
                onSuccess={handleSuccess}
                onCancel={() => {
                  setDialogOpen(false);
                  setSelectedProduct(null);
                }}
              />
            </DialogContent>
          </Dialog>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <Input
              data-testid="search-products-input"
              placeholder="Search products by name or SKU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : products.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package size={48} className="text-gray-400 mb-4" />
              <p className="text-gray-500">No products found</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <Card key={product.id} data-testid={`product-card-${product.sku}`}>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">{product.name}</h3>
                      <p className="text-sm text-gray-500">SKU: {product.sku}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        data-testid={`edit-product-${product.sku}`}
                        onClick={() => {
                          setSelectedProduct(product);
                          setDialogOpen(true);
                        }}
                      >
                        <Edit size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        data-testid={`delete-product-${product.sku}`}
                        onClick={() => handleDelete(product.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Category:</span>
                      <span className="font-medium">{product.category}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Stock:</span>
                      <span
                        className={`font-medium ${
                          product.stock.quantity <= product.stock.reorderPoint
                            ? 'text-red-600'
                            : 'text-green-600'
                        }`}
                      >
                        {product.stock.quantity} {product.unit}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Selling Price:</span>
                      <span className="font-medium">₹{product.pricing.sellingPrice}</span>
                    </div>
                    {product.profitMargin && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Profit Margin:</span>
                        <span className="font-medium text-blue-600">
                          {product.profitMargin.toFixed(2)}%
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
};