import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { useAuth } from '../contexts/AuthContext';
import { productService, customerService, supplierService } from '../api/services';
import axios from '../api/axios';
import {
  Package,
  Users,
  Truck,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  ShoppingCart,
  ArrowUpRight,
  ArrowRight
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  ArcElement
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const StatCard = ({ title, value, icon: Icon, color, subtitle, onClick }) => (
  <Card 
    className={onClick ? "cursor-pointer hover:shadow-lg transition-shadow" : ""}
    onClick={onClick}
  >
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">{value}</h3>
          {subtitle && (
            <p className="text-xs text-gray-500 flex items-center">
              {subtitle}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </CardContent>
  </Card>
);

export const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalCustomers: 0,
    totalSuppliers: 0,
    lowStockCount: 0,
  });
  const [salesStats, setSalesStats] = useState(null);
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [products, customers, suppliers, lowStock] = await Promise.all([
        productService.getProducts({ limit: 1000 }),
        customerService.getCustomers({ limit: 1000 }),
        supplierService.getSuppliers({ limit: 1000 }),
        productService.getLowStockProducts(),
      ]);

      setStats({
        totalProducts: products.length,
        totalCustomers: customers.length,
        totalSuppliers: suppliers.length,
        lowStockCount: lowStock.count || 0,
      });

      setLowStockProducts(lowStock.lowStockItems || []);
      
      // Fetch sales stats
      try {
        const salesResponse = await axios.get('/api/sales/stats');
        setSalesStats(salesResponse.data);
      } catch (error) {
        console.error('Sales stats not available:', error);
      }
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

  // Chart data for top products
  const topProductsChart = salesStats?.topProducts?.length > 0 ? {
    labels: salesStats.topProducts.map(p => p.productName?.substring(0, 15) || 'Unknown'),
    datasets: [
      {
        label: 'Revenue (₹)',
        data: salesStats.topProducts.map(p => p.totalRevenue || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleColor: '#fff',
        bodyColor: '#fff',
        callbacks: {
          label: function(context) {
            return '₹' + context.parsed.y.toLocaleString('en-IN');
          }
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '₹' + value.toLocaleString('en-IN');
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        }
      },
      x: {
        grid: {
          display: false,
        }
      }
    },
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
            <p className="text-gray-600 mt-1">Welcome back, {user?.name}!</p>
          </div>
          <Button onClick={() => navigate('/pos')} size="lg">
            <ShoppingCart className="mr-2 h-5 w-5" />
            Open POS
          </Button>
        </div>

        {/* Sales Stats */}
        {salesStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Sales"
              value={`₹${salesStats.totalSales?.toLocaleString('en-IN', {maximumFractionDigits: 0}) || 0}`}
              icon={DollarSign}
              color="bg-green-500"
              subtitle={`${salesStats.totalTransactions || 0} transactions`}
            />
            <StatCard
              title="Today's Sales"
              value={`₹${salesStats.todaySales?.toLocaleString('en-IN', {maximumFractionDigits: 0}) || 0}`}
              icon={TrendingUp}
              color="bg-blue-500"
              subtitle="Last 24 hours"
            />
            <StatCard
              title="This Week"
              value={`₹${salesStats.weekSales?.toLocaleString('en-IN', {maximumFractionDigits: 0}) || 0}`}
              icon={ArrowUpRight}
              color="bg-purple-500"
              subtitle="Last 7 days"
            />
            <StatCard
              title="This Month"
              value={`₹${salesStats.monthSales?.toLocaleString('en-IN', {maximumFractionDigits: 0}) || 0}`}
              icon={ShoppingCart}
              color="bg-orange-500"
              subtitle="Last 30 days"
            />
          </div>
        )}

        {/* Inventory Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Products"
            value={stats.totalProducts}
            icon={Package}
            color="bg-blue-500"
            onClick={() => navigate('/products')}
          />
          <StatCard
            title="Total Customers"
            value={stats.totalCustomers}
            icon={Users}
            color="bg-green-500"
            onClick={() => navigate('/customers')}
          />
          <StatCard
            title="Total Suppliers"
            value={stats.totalSuppliers}
            icon={Truck}
            color="bg-purple-500"
            onClick={() => navigate('/suppliers')}
          />
          <StatCard
            title="Low Stock Items"
            value={stats.lowStockCount}
            icon={AlertTriangle}
            color="bg-red-500"
            subtitle={stats.lowStockCount > 0 ? "Needs attention" : "All good"}
          />
        </div>

        {/* Charts and Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Products Chart */}
          {topProductsChart && (
            <Card>
              <CardHeader>
                <CardTitle>Top Selling Products</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <Bar data={topProductsChart} options={chartOptions} />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Sales */}
          {salesStats?.recentSales && salesStats.recentSales.length > 0 && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Sales</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => navigate('/sales')}>
                  View All <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {salesStats.recentSales.slice(0, 5).map((sale) => (
                    <div
                      key={sale.id}
                      className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                      onClick={() => navigate('/sales')}
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{sale.invoiceNumber}</p>
                        <p className="text-sm text-gray-600">
                          {sale.customerName || 'Walk-in'} • {sale.items?.length || 0} items
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">₹{sale.total?.toFixed(2)}</p>
                        <Badge variant={sale.paymentStatus === 'paid' ? 'default' : 'secondary'}>
                          {sale.paymentStatus?.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Low Stock Alert */}
          {lowStockProducts.length > 0 && (
            <Card>
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
                          Reorder: {product.stock.reorderPoint}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center"
                  onClick={() => navigate('/pos')}
                >
                  <ShoppingCart className="text-blue-600 mb-2" size={24} />
                  <span className="font-medium">New Sale</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center"
                  onClick={() => navigate('/products')}
                >
                  <Package className="text-green-600 mb-2" size={24} />
                  <span className="font-medium">Add Product</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center"
                  onClick={() => navigate('/customers')}
                >
                  <Users className="text-purple-600 mb-2" size={24} />
                  <span className="font-medium">Add Customer</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center"
                  onClick={() => navigate('/sales')}
                >
                  <DollarSign className="text-orange-600 mb-2" size={24} />
                  <span className="font-medium">View Sales</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};
