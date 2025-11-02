import api from './axios';

export const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async changePassword(currentPassword, newPassword) {
    const response = await api.put('/auth/change-password', {
      currentPassword,
      newPassword,
    });
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export const productService = {
  async getProducts(params = {}) {
    const response = await api.get('/products', { params });
    return response.data;
  },

  async getProduct(id) {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  async createProduct(data) {
    const response = await api.post('/products', data);
    return response.data;
  },

  async updateProduct(id, data) {
    const response = await api.put(`/products/${id}`, data);
    return response.data;
  },

  async deleteProduct(id) {
    const response = await api.delete(`/products/${id}`);
    return response.data;
  },

  async getCategories() {
    const response = await api.get('/products/categories');
    return response.data;
  },

  async getBrands() {
    const response = await api.get('/products/brands');
    return response.data;
  },

  async getLowStockProducts() {
    const response = await api.get('/products/low-stock');
    return response.data;
  },
};

export const customerService = {
  async getCustomers(params = {}) {
    const response = await api.get('/customers', { params });
    return response.data;
  },

  async getCustomer(id) {
    const response = await api.get(`/customers/${id}`);
    return response.data;
  },

  async createCustomer(data) {
    const response = await api.post('/customers', data);
    return response.data;
  },

  async updateCustomer(id, data) {
    const response = await api.put(`/customers/${id}`, data);
    return response.data;
  },

  async deleteCustomer(id) {
    const response = await api.delete(`/customers/${id}`);
    return response.data;
  },
};

export const supplierService = {
  async getSuppliers(params = {}) {
    const response = await api.get('/suppliers', { params });
    return response.data;
  },

  async getSupplier(id) {
    const response = await api.get(`/suppliers/${id}`);
    return response.data;
  },

  async createSupplier(data) {
    const response = await api.post('/suppliers', data);
    return response.data;
  },

  async updateSupplier(id, data) {
    const response = await api.put(`/suppliers/${id}`, data);
    return response.data;
  },

  async deleteSupplier(id) {
    const response = await api.delete(`/suppliers/${id}`);
    return response.data;
  },
};