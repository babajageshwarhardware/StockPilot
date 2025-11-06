import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, Eye, RefreshCw, Filter, FileText, ArrowLeft } from 'lucide-react';
import axios from '../api/axios';
import { useToast } from '../hooks/use-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const Sales = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSale, setSelectedSale] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    paymentStatus: ''
  });
  
  useEffect(() => {
    fetchSales();
  }, []);
  
  const fetchSales = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      if (filters.paymentStatus) params.payment_status = filters.paymentStatus;
      
      const response = await axios.get('/api/sales', { params });
      setSales(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load sales',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const downloadInvoice = async (saleId, invoiceNumber) => {
    try {
      const response = await axios.get(`/api/sales/${saleId}/invoice`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: 'Invoice downloaded successfully'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to download invoice',
        variant: 'destructive'
      });
    }
  };
  
  const viewSaleDetails = async (saleId) => {
    try {
      const response = await axios.get(`/api/sales/${saleId}`);
      setSelectedSale(response.data);
      setShowDetails(true);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load sale details',
        variant: 'destructive'
      });
    }
  };
  
  const getStatusBadge = (status) => {
    const variants = {
      paid: 'default',
      partial: 'secondary',
      pending: 'destructive',
      refunded: 'outline'
    };
    
    return (
      <Badge variant={variants[status] || 'default'}>
        {status.toUpperCase()}
      </Badge>
    );
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/pos')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to POS
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Sales History</h1>
            <p className="text-gray-500">View and manage all sales transactions</p>
          </div>
        </div>
        <Button onClick={fetchSales}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
      
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Start Date</label>
              <Input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({...filters, startDate: e.target.value})}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">End Date</label>
              <Input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({...filters, endDate: e.target.value})}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Payment Status</label>
              <Select
                value={filters.paymentStatus}
                onValueChange={(value) => setFilters({...filters, paymentStatus: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value="paid">Paid</SelectItem>
                  <SelectItem value="partial">Partial</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="refunded">Refunded</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={fetchSales} className="w-full">
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Sales Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500">Loading sales...</p>
            </div>
          ) : sales.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500">No sales found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Invoice</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Items</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Payment</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sales.map((sale) => (
                    <TableRow key={sale.id}>
                      <TableCell className="font-medium">{sale.invoiceNumber}</TableCell>
                      <TableCell>{formatDate(sale.saleDate)}</TableCell>
                      <TableCell>
                        {sale.customerName || 'Walk-in'}
                        {sale.customerPhone && (
                          <div className="text-xs text-gray-500">{sale.customerPhone}</div>
                        )}
                      </TableCell>
                      <TableCell>{sale.items.length} items</TableCell>
                      <TableCell className="font-semibold">₹{sale.total.toFixed(2)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{sale.paymentMode.toUpperCase()}</Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(sale.paymentStatus)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => viewSaleDetails(sale.id)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadInvoice(sale.id, sale.invoiceNumber)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Sale Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Sale Details</DialogTitle>
          </DialogHeader>
          
          {selectedSale && (
            <div className="space-y-4">
              {/* Invoice Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded">
                <div>
                  <p className="text-sm text-gray-600">Invoice Number</p>
                  <p className="font-semibold">{selectedSale.invoiceNumber}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date</p>
                  <p className="font-semibold">{formatDate(selectedSale.saleDate)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Customer</p>
                  <p className="font-semibold">{selectedSale.customerName || 'Walk-in'}</p>
                  {selectedSale.customerPhone && (
                    <p className="text-sm text-gray-500">{selectedSale.customerPhone}</p>
                  )}
                </div>
                <div>
                  <p className="text-sm text-gray-600">Payment Status</p>
                  {getStatusBadge(selectedSale.paymentStatus)}
                </div>
              </div>
              
              {/* Items */}
              <div>
                <h3 className="font-semibold mb-3">Items</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead>SKU</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedSale.items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.productName}</TableCell>
                        <TableCell>{item.sku}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>₹{item.unitPrice.toFixed(2)}</TableCell>
                        <TableCell>₹{item.lineTotal.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              {/* Totals */}
              <div className="space-y-2 p-4 bg-gray-50 rounded">
                <div className="flex justify-between">
                  <span>Subtotal:</span>
                  <span>₹{selectedSale.subtotal.toFixed(2)}</span>
                </div>
                {selectedSale.discountAmount > 0 && (
                  <div className="flex justify-between text-red-600">
                    <span>Discount:</span>
                    <span>-₹{selectedSale.discountAmount.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Tax:</span>
                  <span>₹{selectedSale.taxAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total:</span>
                  <span>₹{selectedSale.total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-green-600">
                  <span>Amount Paid:</span>
                  <span>₹{selectedSale.amountPaid.toFixed(2)}</span>
                </div>
                {selectedSale.amountPaid < selectedSale.total && (
                  <div className="flex justify-between text-red-600 font-semibold">
                    <span>Balance Due:</span>
                    <span>₹{(selectedSale.total - selectedSale.amountPaid).toFixed(2)}</span>
                  </div>
                )}
              </div>
              
              {/* Notes */}
              {selectedSale.notes && (
                <div>
                  <h3 className="font-semibold mb-2">Notes</h3>
                  <p className="text-sm text-gray-600 p-3 bg-gray-50 rounded">{selectedSale.notes}</p>
                </div>
              )}
              
              {/* Download Button */}
              <Button
                className="w-full"
                onClick={() => downloadInvoice(selectedSale.id, selectedSale.invoiceNumber)}
              >
                <Download className="h-4 w-4 mr-2" />
                Download Invoice PDF
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Sales;
