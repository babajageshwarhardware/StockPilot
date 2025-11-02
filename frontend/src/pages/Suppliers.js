import React, { useEffect, useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { supplierService } from '../api/services';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Search, Truck as TruckIcon, Mail, Phone, Star } from 'lucide-react';

const SupplierForm = ({ supplier, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState(
    supplier || {
      name: '',
      email: '',
      phone: '',
      gstNumber: '',
      paymentTerms: 'net30',
      rating: 0,
      address: {
        street: '',
        city: '',
        state: '',
        pincode: '',
        country: 'India',
      },
    }
  );
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (supplier?.id) {
        await supplierService.updateSupplier(supplier.id, formData);
        toast.success('Supplier updated successfully');
      } else {
        await supplierService.createSupplier(formData);
        toast.success('Supplier created successfully');
      }
      onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="supplier-form">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            data-testid="supplier-name-input"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <Label htmlFor="phone">Phone *</Label>
          <Input
            id="phone"
            data-testid="supplier-phone-input"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            pattern="[0-9]{10}"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            data-testid="supplier-email-input"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="gstNumber">GST Number</Label>
          <Input
            id="gstNumber"
            data-testid="supplier-gst-input"
            value={formData.gstNumber}
            onChange={(e) => setFormData({ ...formData, gstNumber: e.target.value })}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Payment Terms</Label>
          <Select
            value={formData.paymentTerms}
            onValueChange={(value) => setFormData({ ...formData, paymentTerms: value })}
          >
            <SelectTrigger data-testid="supplier-payment-terms-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="immediate">Immediate</SelectItem>
              <SelectItem value="net15">Net 15</SelectItem>
              <SelectItem value="net30">Net 30</SelectItem>
              <SelectItem value="net60">Net 60</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="rating">Rating (1-5)</Label>
          <Input
            id="rating"
            type="number"
            data-testid="supplier-rating-input"
            min="1"
            max="5"
            step="0.5"
            value={formData.rating}
            onChange={(e) => setFormData({ ...formData, rating: parseFloat(e.target.value) })}
          />
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="font-semibold mb-3">Address</h3>
        <div className="space-y-3">
          <div>
            <Label htmlFor="street">Street</Label>
            <Input
              id="street"
              data-testid="supplier-street-input"
              value={formData.address.street}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  address: { ...formData.address, street: e.target.value },
                })
              }
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                data-testid="supplier-city-input"
                value={formData.address.city}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    address: { ...formData.address, city: e.target.value },
                  })
                }
              />
            </div>
            <div>
              <Label htmlFor="state">State</Label>
              <Input
                id="state"
                data-testid="supplier-state-input"
                value={formData.address.state}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    address: { ...formData.address, state: e.target.value },
                  })
                }
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="pincode">Pincode</Label>
              <Input
                id="pincode"
                data-testid="supplier-pincode-input"
                value={formData.address.pincode}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    address: { ...formData.address, pincode: e.target.value },
                  })
                }
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" data-testid="supplier-submit-btn" disabled={loading}>
          {loading ? 'Saving...' : supplier?.id ? 'Update Supplier' : 'Create Supplier'}
        </Button>
      </div>
    </form>
  );
};

export const Suppliers = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState(null);

  useEffect(() => {
    fetchSuppliers();
  }, [search]);

  const fetchSuppliers = async () => {
    try {
      const data = await supplierService.getSuppliers({ search, limit: 100 });
      setSuppliers(data);
    } catch (error) {
      toast.error('Failed to fetch suppliers');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      try {
        await supplierService.deleteSupplier(id);
        toast.success('Supplier deleted successfully');
        fetchSuppliers();
      } catch (error) {
        toast.error('Failed to delete supplier');
      }
    }
  };

  const handleSuccess = () => {
    setDialogOpen(false);
    setSelectedSupplier(null);
    fetchSuppliers();
  };

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="suppliers-page">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Suppliers</h2>
            <p className="text-gray-600 mt-1">Manage your suppliers</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button
                data-testid="add-supplier-btn"
                onClick={() => {
                  setSelectedSupplier(null);
                  setDialogOpen(true);
                }}
              >
                <Plus size={20} className="mr-2" />
                Add Supplier
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {selectedSupplier ? 'Edit Supplier' : 'Add New Supplier'}
                </DialogTitle>
              </DialogHeader>
              <SupplierForm
                supplier={selectedSupplier}
                onSuccess={handleSuccess}
                onCancel={() => {
                  setDialogOpen(false);
                  setSelectedSupplier(null);
                }}
              />
            </DialogContent>
          </Dialog>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <Input
              data-testid="search-suppliers-input"
              placeholder="Search suppliers by name, phone, or email..."
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
        ) : suppliers.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <TruckIcon size={48} className="text-gray-400 mb-4" />
              <p className="text-gray-500">No suppliers found</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {suppliers.map((supplier) => (
              <Card key={supplier.id} data-testid={`supplier-card-${supplier.phone}`}>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">{supplier.name}</h3>
                      {supplier.rating > 0 && (
                        <div className="flex items-center mt-1">
                          <Star size={14} className="text-yellow-500 fill-yellow-500" />
                          <span className="text-sm text-gray-600 ml-1">{supplier.rating}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        data-testid={`edit-supplier-${supplier.phone}`}
                        onClick={() => {
                          setSelectedSupplier(supplier);
                          setDialogOpen(true);
                        }}
                      >
                        <Edit size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        data-testid={`delete-supplier-${supplier.phone}`}
                        onClick={() => handleDelete(supplier.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone size={14} className="mr-2" />
                      {supplier.phone}
                    </div>
                    {supplier.email && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Mail size={14} className="mr-2" />
                        {supplier.email}
                      </div>
                    )}
                    {supplier.address?.city && (
                      <div className="text-sm text-gray-600">
                        {supplier.address.city}, {supplier.address.state}
                      </div>
                    )}
                    <div className="flex justify-between text-sm pt-2 border-t">
                      <span className="text-gray-600">Payment Terms:</span>
                      <span className="font-medium capitalize">
                        {supplier.paymentTerms.replace('net', 'Net ')}
                      </span>
                    </div>
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