import React, { useEffect, useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { productService, customerService, supplierService } from '../api/services';
import { Package, Users, Truck, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const StatCard = ({ title, value, icon: Icon, color, trend }) => (
  <Card data-testid={`stat-card-${title.toLowerCase().replace(/\s/g, '-')}`}>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {trend && (
        <p className="text-xs text-green-600 flex items-center mt-1">
          <TrendingUp size={12} className="mr-1" />
          {trend}
        </p>
      )}
    </CardContent>
  </Card>
);

export const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalCustomers: 0,
    totalSuppliers: 0,
    lowStockCount: 0,
  });
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [products, customers, suppliers, lowStock] = await Promise.all([
        productService.getProducts({ limit: 100 }),
        customerService.getCustomers({ limit: 100 }),
        supplierService.getSuppliers({ limit: 100 }),
        productService.getLowStockProducts(),
      ]);

      setStats({
        totalProducts: products.length,
        totalCustomers: customers.length,
        totalSuppliers: suppliers.length,
        lowStockCount: lowStock.count,
      });

      setLowStockProducts(lowStock.lowStockItems || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="dashboard-page">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">Welcome back, {user?.name}!</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Products"
            value={stats.totalProducts}
            icon={Package}
            color="bg-blue-500"
          />
          <StatCard
            title="Total Customers"
            value={stats.totalCustomers}
            icon={Users}
            color="bg-green-500"
          />
          <StatCard
            title="Total Suppliers"
            value={stats.totalSuppliers}
            icon={Truck}
            color="bg-purple-500"
          />
          <StatCard
            title="Low Stock Items"
            value={stats.lowStockCount}
            icon={AlertTriangle}
            color="bg-red-500"
          />
        </div>

        {lowStockProducts.length > 0 && (
          <Card data-testid="low-stock-section">
            <CardHeader>
              <CardTitle className="flex items-center text-red-600">
                <AlertTriangle size={20} className="mr-2" />
                Low Stock Alert
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {lowStockProducts.slice(0, 5).map((product) => (
                  <div
                    key={product.id}
                    data-testid={`low-stock-item-${product.sku}`}
                    className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-100"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{product.name}</p>
                      <p className="text-sm text-gray-600">SKU: {product.sku}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-red-600">
                        Stock: {product.stock.quantity}
                      </p>
                      <p className="text-xs text-gray-500">
                        Reorder at: {product.stock.reorderPoint}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <a
                  href="/products"
                  className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-100 transition-colors"
                >
                  <Package className="text-blue-600 mb-2" size={24} />
                  <p className="font-medium text-gray-900">Add Product</p>
                </a>
                <a
                  href="/customers"
                  className="p-4 bg-green-50 hover:bg-green-100 rounded-lg border border-green-100 transition-colors"
                >
                  <Users className="text-green-600 mb-2" size={24} />
                  <p className="font-medium text-gray-900">Add Customer</p>
                </a>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Your Role:</span>
                  <span className="font-medium text-gray-900 capitalize">
                    {user?.role?.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Account Status:</span>
                  <span className="font-medium text-green-600">Active</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Login:</span>
                  <span className="font-medium text-gray-900">
                    {user?.lastLogin
                      ? new Date(user.lastLogin).toLocaleDateString()
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};