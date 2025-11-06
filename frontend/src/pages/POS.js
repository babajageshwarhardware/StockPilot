import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Minus, Trash2, ShoppingCart, X, User, CreditCard, Wallet } from 'lucide-react';
import axios from '../api/axios';
import { useToast } from '../hooks/use-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';

const POS = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [cart, setCart] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Checkout form
  const [paymentMode, setPaymentMode] = useState('cash');
  const [discountType, setDiscountType] = useState('fixed');
  const [discountAmount, setDiscountAmount] = useState(0);
  const [amountPaid, setAmountPaid] = useState(0);
  const [notes, setNotes] = useState('');
  
  useEffect(() => {
    fetchProducts();
    fetchCustomers();
  }, []);
  
  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/products');
      setProducts(response.data.filter(p => p.isActive && p.stock.quantity > 0));
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load products',
        variant: 'destructive'
      });
    }
  };
  
  const fetchCustomers = async () => {
    try {
      const response = await axios.get('/api/customers');
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    }
  };
  
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (product.barcode && product.barcode.toLowerCase().includes(searchTerm.toLowerCase()))
  );
  
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.productId === product.id);
    
    if (existingItem) {
      if (existingItem.quantity >= product.stock.quantity) {
        toast({
          title: 'Stock Limit',
          description: `Only ${product.stock.quantity} units available`,
          variant: 'destructive'
        });
        return;
      }
      updateQuantity(product.id, existingItem.quantity + 1);
    } else {
      const newItem = {
        productId: product.id,
        productName: product.name,
        sku: product.sku,
        quantity: 1,
        unitPrice: product.pricing.sellingPrice,
        discount: 0,
        discountType: 'fixed',
        taxRate: product.pricing.taxRate || 0,
        taxAmount: 0,
        lineTotal: product.pricing.sellingPrice,
        maxStock: product.stock.quantity
      };
      calculateLineTotal(newItem);
      setCart([...cart, newItem]);
    }
  };
  
  const updateQuantity = (productId, newQuantity) => {
    setCart(cart.map(item => {
      if (item.productId === productId) {
        if (newQuantity > item.maxStock) {
          toast({
            title: 'Stock Limit',
            description: `Only ${item.maxStock} units available`,
            variant: 'destructive'
          });
          return item;
        }
        if (newQuantity <= 0) {
          return null;
        }
        const updatedItem = { ...item, quantity: newQuantity };
        calculateLineTotal(updatedItem);
        return updatedItem;
      }
      return item;
    }).filter(Boolean));
  };
  
  const updateItemDiscount = (productId, discount, type) => {
    setCart(cart.map(item => {
      if (item.productId === productId) {
        const updatedItem = { ...item, discount, discountType: type };
        calculateLineTotal(updatedItem);
        return updatedItem;
      }
      return item;
    }));
  };
  
  const calculateLineTotal = (item) => {
    const subtotal = item.unitPrice * item.quantity;
    let discountValue = 0;
    
    if (item.discountType === 'percentage') {
      discountValue = (subtotal * item.discount) / 100;
    } else {
      discountValue = item.discount;
    }
    
    const afterDiscount = subtotal - discountValue;
    const taxAmount = (afterDiscount * item.taxRate) / 100;
    item.taxAmount = taxAmount;
    item.lineTotal = afterDiscount + taxAmount;
  };
  
  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.productId !== productId));
  };
  
  const calculateTotals = () => {
    const subtotal = cart.reduce((sum, item) => {
      const itemSubtotal = item.unitPrice * item.quantity;
      const itemDiscount = item.discountType === 'percentage' 
        ? (itemSubtotal * item.discount) / 100 
        : item.discount;
      return sum + (itemSubtotal - itemDiscount);
    }, 0);
    
    let cartDiscount = 0;
    if (discountType === 'percentage') {
      cartDiscount = (subtotal * discountAmount) / 100;
    } else {
      cartDiscount = discountAmount;
    }
    
    const afterDiscount = subtotal - cartDiscount;
    const totalTax = cart.reduce((sum, item) => sum + item.taxAmount, 0);
    const total = afterDiscount + totalTax;
    
    return {
      subtotal: cart.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0),
      discount: cartDiscount,
      tax: totalTax,
      total: total
    };
  };
  
  const handleCheckout = async () => {
    if (cart.length === 0) {
      toast({
        title: 'Empty Cart',
        description: 'Please add items to cart',
        variant: 'destructive'
      });
      return;
    }
    
    setLoading(true);
    try {
      const totals = calculateTotals();
      const paidAmount = parseFloat(amountPaid) || totals.total;
      
      const saleData = {
        customerId: selectedCustomer?.id || null,
        customerName: selectedCustomer?.name || null,
        customerPhone: selectedCustomer?.phone || null,
        items: cart,
        subtotal: totals.subtotal,
        discountAmount: totals.discount,
        discountType: discountType,
        taxAmount: totals.tax,
        total: totals.total,
        amountPaid: paidAmount,
        paymentMode: paymentMode,
        paymentStatus: paidAmount >= totals.total ? 'paid' : 'partial',
        notes: notes
      };
      
      const response = await axios.post('/api/sales', saleData);
      
      toast({
        title: 'Success',
        description: `Sale completed! Invoice: ${response.data.invoiceNumber}`,
      });
      
      // Download invoice
      const invoiceResponse = await axios.get(`/api/sales/${response.data.id}/invoice`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([invoiceResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${response.data.invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Reset
      setCart([]);
      setSelectedCustomer(null);
      setDiscountAmount(0);
      setAmountPaid(0);
      setNotes('');
      setShowCheckout(false);
      fetchProducts(); // Refresh stock
      
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to complete sale',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const totals = calculateTotals();
  
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Point of Sale</h1>
          <Button variant="outline" onClick={() => navigate('/sales')}>
            View Sales History
          </Button>
        </div>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Products Section */}
        <div className="flex-1 flex flex-col p-4 overflow-hidden">
          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search products by name, SKU, or barcode..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          {/* Products Grid */}
          <div className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {filteredProducts.map(product => (
                <Card
                  key={product.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => addToCart(product)}
                >
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-sm line-clamp-2">{product.name}</h3>
                      <p className="text-xs text-gray-500">{product.sku}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-bold text-green-600">
                          ₹{product.pricing.sellingPrice}
                        </span>
                        <Badge variant={product.stock.quantity < 10 ? "destructive" : "secondary"}>
                          {product.stock.quantity} {product.unit}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
        
        {/* Cart Section */}
        <div className="w-96 bg-white border-l flex flex-col">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                Cart ({cart.length})
              </span>
              {cart.length > 0 && (
                <Button variant="ghost" size="sm" onClick={() => setCart([])}>
                  Clear All
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {cart.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <ShoppingCart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Cart is empty</p>
              </div>
            ) : (
              cart.map(item => (
                <Card key={item.productId}>
                  <CardContent className="p-3 space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm">{item.productName}</h4>
                        <p className="text-xs text-gray-500">{item.sku}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFromCart(item.productId)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                        >
                          <Minus className="h-3 w-3" />
                        </Button>
                        <span className="w-8 text-center font-semibold">{item.quantity}</span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                      <span className="font-semibold">₹{item.lineTotal.toFixed(2)}</span>
                    </div>
                    
                    <div className="text-xs text-gray-600">
                      ₹{item.unitPrice} × {item.quantity}
                      {item.taxRate > 0 && ` + ${item.taxRate}% tax`}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          
          {/* Customer Selection */}
          <div className="border-t p-4">
            <Label className="text-xs mb-2 block">Customer (Optional)</Label>
            <Select
              value={selectedCustomer?.id || ''}
              onValueChange={(value) => {
                const customer = customers.find(c => c.id === value);
                setSelectedCustomer(customer || null);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Walk-in Customer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="walk-in">Walk-in Customer</SelectItem>
                {customers.map(customer => (
                  <SelectItem key={customer.id} value={customer.id}>
                    {customer.name} - {customer.phone}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Totals */}
          <div className="border-t p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span>Subtotal:</span>
              <span>₹{totals.subtotal.toFixed(2)}</span>
            </div>
            {totals.discount > 0 && (
              <div className="flex justify-between text-sm text-red-600">
                <span>Discount:</span>
                <span>-₹{totals.discount.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span>Tax:</span>
              <span>₹{totals.tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t pt-2">
              <span>Total:</span>
              <span className="text-green-600">₹{totals.total.toFixed(2)}</span>
            </div>
          </div>
          
          {/* Checkout Button */}
          <div className="p-4 border-t">
            <Button
              className="w-full"
              size="lg"
              disabled={cart.length === 0}
              onClick={() => {
                setAmountPaid(totals.total);
                setShowCheckout(true);
              }}
            >
              <CreditCard className="mr-2 h-5 w-5" />
              Checkout
            </Button>
          </div>
        </div>
      </div>
      
      {/* Checkout Dialog */}
      <Dialog open={showCheckout} onOpenChange={setShowCheckout}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Complete Payment</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label>Payment Mode</Label>
              <Select value={paymentMode} onValueChange={setPaymentMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">Cash</SelectItem>
                  <SelectItem value="card">Card</SelectItem>
                  <SelectItem value="upi">UPI</SelectItem>
                  <SelectItem value="net_banking">Net Banking</SelectItem>
                  <SelectItem value="wallet">Wallet</SelectItem>
                  <SelectItem value="credit">Credit</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Discount Type</Label>
                <Select value={discountType} onValueChange={setDiscountType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fixed">Fixed (₹)</SelectItem>
                    <SelectItem value="percentage">Percentage (%)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Discount</Label>
                <Input
                  type="number"
                  min="0"
                  value={discountAmount}
                  onChange={(e) => setDiscountAmount(parseFloat(e.target.value) || 0)}
                />
              </div>
            </div>
            
            <div>
              <Label>Amount Paid</Label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={amountPaid}
                onChange={(e) => setAmountPaid(parseFloat(e.target.value) || 0)}
              />
            </div>
            
            <div>
              <Label>Notes (Optional)</Label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes for this sale..."
                rows={2}
              />
            </div>
            
            <div className="bg-gray-50 p-4 rounded space-y-1">
              <div className="flex justify-between font-semibold">
                <span>Total Amount:</span>
                <span>₹{totals.total.toFixed(2)}</span>
              </div>
              {amountPaid < totals.total && (
                <div className="flex justify-between text-sm text-red-600">
                  <span>Balance Due:</span>
                  <span>₹{(totals.total - amountPaid).toFixed(2)}</span>
                </div>
              )}
              {amountPaid > totals.total && (
                <div className="flex justify-between text-sm text-green-600">
                  <span>Change:</span>
                  <span>₹{(amountPaid - totals.total).toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCheckout(false)}>
              Cancel
            </Button>
            <Button onClick={handleCheckout} disabled={loading}>
              {loading ? 'Processing...' : 'Complete Sale'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default POS;
