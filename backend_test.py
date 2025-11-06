#!/usr/bin/env python3
"""
Backend Testing Script for StockPilot Sales/POS System
Tests all sales-related API endpoints and functionality
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Get backend URL from frontend .env
BACKEND_URL = "https://pos-master-25.preview.emergentagent.com/api"

class SalesAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.created_sales = []
        self.products = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "admin@stockpilot.com",
                    "password": "Admin@123456"
                },
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                self.log_test("Authentication", True, "Successfully logged in")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_products(self) -> bool:
        """Get available products for testing"""
        try:
            response = requests.get(f"{self.base_url}/products", headers=self.headers)
            
            if response.status_code == 200:
                self.products = response.json()
                if len(self.products) > 0:
                    self.log_test("Get Products", True, f"Retrieved {len(self.products)} products")
                    return True
                else:
                    self.log_test("Get Products", False, "No products found in database")
                    return False
            else:
                self.log_test("Get Products", False, f"Failed to get products: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Products", False, f"Error getting products: {str(e)}")
            return False
    
    def test_sales_stats_empty(self) -> bool:
        """Test sales statistics before any sales exist"""
        try:
            response = requests.get(f"{self.base_url}/sales/stats", headers=self.headers)
            
            if response.status_code == 200:
                stats = response.json()
                expected_fields = ["totalSales", "todaySales", "weekSales", "monthSales", "topProducts", "recentSales"]
                
                missing_fields = [field for field in expected_fields if field not in stats]
                if missing_fields:
                    self.log_test("Sales Stats (Empty)", False, f"Missing fields: {missing_fields}", stats)
                    return False
                
                # Check if stats are properly initialized
                if (stats["totalSales"] == 0 and 
                    stats["todaySales"] == 0 and 
                    len(stats["topProducts"]) == 0 and 
                    len(stats["recentSales"]) == 0):
                    self.log_test("Sales Stats (Empty)", True, "Stats properly initialized with zero values")
                    return True
                else:
                    self.log_test("Sales Stats (Empty)", False, "Stats not properly initialized", stats)
                    return False
            else:
                self.log_test("Sales Stats (Empty)", False, f"Failed to get stats: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Sales Stats (Empty)", False, f"Error getting stats: {str(e)}")
            return False
    
    def create_test_sale(self, test_name: str, sale_data: Dict) -> Dict:
        """Create a test sale"""
        try:
            response = requests.post(f"{self.base_url}/sales", json=sale_data, headers=self.headers)
            
            if response.status_code == 201:
                sale = response.json()
                self.created_sales.append(sale)
                
                # Verify required fields
                required_fields = ["id", "invoiceNumber", "saleDate", "total", "items"]
                missing_fields = [field for field in required_fields if field not in sale]
                
                if missing_fields:
                    self.log_test(test_name, False, f"Missing fields in response: {missing_fields}")
                    return None
                
                # Verify invoice number format (INV-YYYYMMDD-XXXX)
                invoice_num = sale["invoiceNumber"]
                if not invoice_num.startswith("INV-") or len(invoice_num) != 17:
                    self.log_test(test_name, False, f"Invalid invoice number format: {invoice_num}")
                    return None
                
                self.log_test(test_name, True, f"Sale created successfully. Invoice: {invoice_num}")
                return sale
            else:
                self.log_test(test_name, False, f"Failed to create sale: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(test_name, False, f"Error creating sale: {str(e)}")
            return None
    
    def test_single_item_sale(self) -> bool:
        """Test creating a sale with single item"""
        if not self.products:
            return False
            
        product = self.products[0]
        sale_data = {
            "customerId": None,
            "customerName": "John Smith",
            "customerPhone": "+1234567890",
            "items": [{
                "productId": product["id"],
                "productName": product["name"],
                "sku": product["sku"],
                "quantity": 2.0,
                "unitPrice": product["price"],
                "discount": 0,
                "discountType": "fixed",
                "taxRate": 18.0,
                "taxAmount": product["price"] * 2 * 0.18,
                "lineTotal": product["price"] * 2 * 1.18
            }],
            "subtotal": product["price"] * 2,
            "discountAmount": 0,
            "discountType": "fixed",
            "taxAmount": product["price"] * 2 * 0.18,
            "total": product["price"] * 2 * 1.18,
            "amountPaid": product["price"] * 2 * 1.18,
            "paymentMode": "cash",
            "paymentStatus": "paid",
            "notes": "Test single item sale"
        }
        
        sale = self.create_test_sale("Single Item Sale", sale_data)
        return sale is not None
    
    def test_multiple_items_sale(self) -> bool:
        """Test creating a sale with multiple items"""
        if len(self.products) < 2:
            self.log_test("Multiple Items Sale", False, "Need at least 2 products for this test")
            return False
            
        items = []
        subtotal = 0
        
        for i in range(min(3, len(self.products))):
            product = self.products[i]
            quantity = 1.0 + i
            line_total = product["price"] * quantity
            
            items.append({
                "productId": product["id"],
                "productName": product["name"],
                "sku": product["sku"],
                "quantity": quantity,
                "unitPrice": product["price"],
                "discount": 0,
                "discountType": "fixed",
                "taxRate": 0,
                "taxAmount": 0,
                "lineTotal": line_total
            })
            subtotal += line_total
        
        sale_data = {
            "customerId": None,
            "customerName": "Jane Doe",
            "customerPhone": "+1987654321",
            "items": items,
            "subtotal": subtotal,
            "discountAmount": 0,
            "discountType": "fixed",
            "taxAmount": 0,
            "total": subtotal,
            "amountPaid": subtotal,
            "paymentMode": "card",
            "paymentStatus": "paid",
            "notes": "Test multiple items sale"
        }
        
        sale = self.create_test_sale("Multiple Items Sale", sale_data)
        return sale is not None
    
    def test_sale_with_discount(self) -> bool:
        """Test creating a sale with discount"""
        if not self.products:
            return False
            
        product = self.products[0]
        subtotal = product["price"] * 3
        discount = 50.0  # Fixed discount
        total = subtotal - discount
        
        sale_data = {
            "customerId": None,
            "customerName": "Bob Wilson",
            "customerPhone": "+1122334455",
            "items": [{
                "productId": product["id"],
                "productName": product["name"],
                "sku": product["sku"],
                "quantity": 3.0,
                "unitPrice": product["price"],
                "discount": 0,
                "discountType": "fixed",
                "taxRate": 0,
                "taxAmount": 0,
                "lineTotal": subtotal
            }],
            "subtotal": subtotal,
            "discountAmount": discount,
            "discountType": "fixed",
            "taxAmount": 0,
            "total": total,
            "amountPaid": total,
            "paymentMode": "upi",
            "paymentStatus": "paid",
            "notes": "Test sale with fixed discount"
        }
        
        sale = self.create_test_sale("Sale with Discount", sale_data)
        return sale is not None
    
    def test_insufficient_stock(self) -> bool:
        """Test creating a sale with insufficient stock"""
        if not self.products:
            return False
            
        product = self.products[0]
        # Try to sell a very large quantity to trigger stock error
        large_quantity = 999999.0
        
        sale_data = {
            "customerId": None,
            "customerName": "Test Customer",
            "items": [{
                "productId": product["id"],
                "productName": product["name"],
                "sku": product["sku"],
                "quantity": large_quantity,
                "unitPrice": product["price"],
                "discount": 0,
                "discountType": "fixed",
                "taxRate": 0,
                "taxAmount": 0,
                "lineTotal": product["price"] * large_quantity
            }],
            "subtotal": product["price"] * large_quantity,
            "discountAmount": 0,
            "discountType": "fixed",
            "taxAmount": 0,
            "total": product["price"] * large_quantity,
            "amountPaid": product["price"] * large_quantity,
            "paymentMode": "cash",
            "paymentStatus": "paid"
        }
        
        try:
            response = requests.post(f"{self.base_url}/sales", json=sale_data, headers=self.headers)
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "Insufficient stock" in error_msg:
                    self.log_test("Insufficient Stock Validation", True, "Correctly rejected sale with insufficient stock")
                    return True
                else:
                    self.log_test("Insufficient Stock Validation", False, f"Wrong error message: {error_msg}")
                    return False
            else:
                self.log_test("Insufficient Stock Validation", False, f"Expected 400 error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Insufficient Stock Validation", False, f"Error testing insufficient stock: {str(e)}")
            return False
    
    def test_list_sales(self) -> bool:
        """Test listing sales with various filters"""
        try:
            # Test basic listing
            response = requests.get(f"{self.base_url}/sales", headers=self.headers)
            
            if response.status_code == 200:
                sales = response.json()
                if len(sales) >= len(self.created_sales):
                    self.log_test("List Sales", True, f"Retrieved {len(sales)} sales")
                else:
                    self.log_test("List Sales", False, f"Expected at least {len(self.created_sales)} sales, got {len(sales)}")
                    return False
            else:
                self.log_test("List Sales", False, f"Failed to list sales: {response.status_code}", response.text)
                return False
            
            # Test with date filter
            today = datetime.now().strftime("%Y-%m-%d")
            response = requests.get(
                f"{self.base_url}/sales?start_date={today}T00:00:00Z&end_date={today}T23:59:59Z",
                headers=self.headers
            )
            
            if response.status_code == 200:
                filtered_sales = response.json()
                self.log_test("List Sales with Date Filter", True, f"Retrieved {len(filtered_sales)} sales for today")
            else:
                self.log_test("List Sales with Date Filter", False, f"Date filter failed: {response.status_code}")
                return False
            
            # Test pagination
            response = requests.get(f"{self.base_url}/sales?skip=0&limit=2", headers=self.headers)
            
            if response.status_code == 200:
                paginated_sales = response.json()
                if len(paginated_sales) <= 2:
                    self.log_test("List Sales Pagination", True, f"Pagination working, got {len(paginated_sales)} sales")
                else:
                    self.log_test("List Sales Pagination", False, f"Pagination failed, expected max 2, got {len(paginated_sales)}")
                    return False
            else:
                self.log_test("List Sales Pagination", False, f"Pagination failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("List Sales", False, f"Error listing sales: {str(e)}")
            return False
    
    def test_get_single_sale(self) -> bool:
        """Test retrieving a single sale by ID"""
        if not self.created_sales:
            self.log_test("Get Single Sale", False, "No sales created to test")
            return False
            
        try:
            sale_id = self.created_sales[0]["id"]
            response = requests.get(f"{self.base_url}/sales/{sale_id}", headers=self.headers)
            
            if response.status_code == 200:
                sale = response.json()
                if sale["id"] == sale_id:
                    self.log_test("Get Single Sale", True, f"Retrieved sale {sale_id}")
                    return True
                else:
                    self.log_test("Get Single Sale", False, f"ID mismatch: expected {sale_id}, got {sale['id']}")
                    return False
            else:
                self.log_test("Get Single Sale", False, f"Failed to get sale: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Single Sale", False, f"Error getting sale: {str(e)}")
            return False
    
    def test_invoice_pdf_generation(self) -> bool:
        """Test invoice PDF generation"""
        if not self.created_sales:
            self.log_test("Invoice PDF Generation", False, "No sales created to test")
            return False
            
        try:
            sale_id = self.created_sales[0]["id"]
            response = requests.get(f"{self.base_url}/sales/{sale_id}/invoice", headers=self.headers)
            
            if response.status_code == 200:
                # Check if response is PDF
                content_type = response.headers.get("content-type", "")
                if "application/pdf" in content_type:
                    # Check Content-Disposition header
                    disposition = response.headers.get("content-disposition", "")
                    if "attachment" in disposition and "filename=" in disposition:
                        pdf_size = len(response.content)
                        self.log_test("Invoice PDF Generation", True, f"PDF generated successfully ({pdf_size} bytes)")
                        return True
                    else:
                        self.log_test("Invoice PDF Generation", False, f"Missing or invalid Content-Disposition header: {disposition}")
                        return False
                else:
                    self.log_test("Invoice PDF Generation", False, f"Invalid content type: {content_type}")
                    return False
            else:
                self.log_test("Invoice PDF Generation", False, f"Failed to generate PDF: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Invoice PDF Generation", False, f"Error generating PDF: {str(e)}")
            return False
    
    def test_update_sale(self) -> bool:
        """Test updating sale details"""
        if not self.created_sales:
            self.log_test("Update Sale", False, "No sales created to test")
            return False
            
        try:
            sale_id = self.created_sales[0]["id"]
            update_data = {
                "paymentStatus": "partial",
                "amountPaid": 100.0,
                "notes": "Updated payment status and notes"
            }
            
            response = requests.put(f"{self.base_url}/sales/{sale_id}", json=update_data, headers=self.headers)
            
            if response.status_code == 200:
                updated_sale = response.json()
                if (updated_sale["paymentStatus"] == "partial" and 
                    updated_sale["amountPaid"] == 100.0 and
                    updated_sale["notes"] == "Updated payment status and notes"):
                    self.log_test("Update Sale", True, "Sale updated successfully")
                    return True
                else:
                    self.log_test("Update Sale", False, "Sale not updated correctly", updated_sale)
                    return False
            else:
                self.log_test("Update Sale", False, f"Failed to update sale: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Update Sale", False, f"Error updating sale: {str(e)}")
            return False
    
    def test_sales_stats_after_sales(self) -> bool:
        """Test sales statistics after creating sales"""
        try:
            response = requests.get(f"{self.base_url}/sales/stats", headers=self.headers)
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check if stats are updated
                if (stats["totalSales"] > 0 and 
                    stats["totalTransactions"] > 0 and
                    len(stats["recentSales"]) > 0):
                    self.log_test("Sales Stats (After Sales)", True, f"Stats updated: {stats['totalSales']:.2f} total sales, {stats['totalTransactions']} transactions")
                    return True
                else:
                    self.log_test("Sales Stats (After Sales)", False, "Stats not properly updated", stats)
                    return False
            else:
                self.log_test("Sales Stats (After Sales)", False, f"Failed to get stats: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Sales Stats (After Sales)", False, f"Error getting stats: {str(e)}")
            return False
    
    def test_error_scenarios(self) -> bool:
        """Test various error scenarios"""
        success_count = 0
        total_tests = 0
        
        # Test invalid sale ID
        try:
            total_tests += 1
            response = requests.get(f"{self.base_url}/sales/invalid-id", headers=self.headers)
            if response.status_code == 404:
                self.log_test("Error: Invalid Sale ID", True, "Correctly returned 404 for invalid sale ID")
                success_count += 1
            else:
                self.log_test("Error: Invalid Sale ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error: Invalid Sale ID", False, f"Error: {str(e)}")
        
        # Test missing required fields
        try:
            total_tests += 1
            invalid_sale = {"items": []}  # Missing required fields
            response = requests.post(f"{self.base_url}/sales", json=invalid_sale, headers=self.headers)
            if response.status_code in [400, 422]:
                self.log_test("Error: Missing Required Fields", True, "Correctly rejected sale with missing fields")
                success_count += 1
            else:
                self.log_test("Error: Missing Required Fields", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_test("Error: Missing Required Fields", False, f"Error: {str(e)}")
        
        # Test invalid product ID
        try:
            total_tests += 1
            invalid_sale = {
                "items": [{
                    "productId": "invalid-product-id",
                    "productName": "Test Product",
                    "sku": "TEST",
                    "quantity": 1.0,
                    "unitPrice": 100.0,
                    "discount": 0,
                    "discountType": "fixed",
                    "taxRate": 0,
                    "taxAmount": 0,
                    "lineTotal": 100.0
                }],
                "subtotal": 100.0,
                "discountAmount": 0,
                "discountType": "fixed",
                "taxAmount": 0,
                "total": 100.0,
                "amountPaid": 100.0,
                "paymentMode": "cash",
                "paymentStatus": "paid"
            }
            response = requests.post(f"{self.base_url}/sales", json=invalid_sale, headers=self.headers)
            if response.status_code == 404:
                self.log_test("Error: Invalid Product ID", True, "Correctly rejected sale with invalid product ID")
                success_count += 1
            else:
                self.log_test("Error: Invalid Product ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error: Invalid Product ID", False, f"Error: {str(e)}")
        
        return success_count == total_tests
    
    def run_all_tests(self):
        """Run all sales API tests"""
        print("🚀 Starting StockPilot Sales/POS Backend Tests")
        print("=" * 60)
        
        # Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Get products for testing
        if not self.get_products():
            print("❌ No products available. Cannot proceed with sales tests.")
            return
        
        # Run tests in order
        test_methods = [
            self.test_sales_stats_empty,
            self.test_single_item_sale,
            self.test_multiple_items_sale,
            self.test_sale_with_discount,
            self.test_insufficient_stock,
            self.test_list_sales,
            self.test_get_single_sale,
            self.test_invoice_pdf_generation,
            self.test_update_sale,
            self.test_sales_stats_after_sales,
            self.test_error_scenarios
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Test method failed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        print(f"\n📝 Created {len(self.created_sales)} test sales")
        if self.created_sales:
            print("Invoice Numbers:")
            for sale in self.created_sales:
                print(f"  - {sale['invoiceNumber']}")

if __name__ == "__main__":
    tester = SalesAPITester()
    tester.run_all_tests()