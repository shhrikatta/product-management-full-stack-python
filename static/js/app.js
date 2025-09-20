// Product Management App JavaScript
class ProductManager {
    constructor() {
        this.apiBaseUrl = window.location.origin + '/api/products';
        this.products = [];
        this.filteredProducts = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadProducts();
    }

    setupEventListeners() {
        // Add product form
        document.getElementById('add-product-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addProduct();
        });

        // Edit product form
        document.getElementById('edit-product-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProduct();
        });

        // Search functionality
        document.getElementById('search-input').addEventListener('input', () => {
            this.filterProducts();
        });

        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeAllModals();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    // API Methods
    async apiRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async loadProducts() {
        try {
            this.showLoading(true);
            this.hideEmptyState();

            const data = await this.apiRequest(this.apiBaseUrl);
            this.products = Array.isArray(data) ? data : [];
            this.filteredProducts = [...this.products];
            
            this.renderProducts();
            this.updateProductCount();
            
            if (this.products.length === 0) {
                this.showEmptyState();
            }
        } catch (error) {
            this.showAlert('Error loading products: ' + error.message, 'error');
            this.showEmptyState();
        } finally {
            this.showLoading(false);
        }
    }

    async addProduct() {
        const form = document.getElementById('add-product-form');
        const formData = new FormData(form);
        
        const productData = {
            name: formData.get('name').trim(),
            price: parseFloat(formData.get('price')),
            quantity: parseInt(formData.get('quantity'))
        };

        // Client-side validation
        if (!this.validateProduct(productData)) {
            return;
        }

        try {
            const addButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(addButton, true);

            const newProduct = await this.apiRequest(this.apiBaseUrl, {
                method: 'POST',
                body: JSON.stringify(productData)
            });

            this.products.unshift(newProduct);
            this.filteredProducts = [...this.products];
            this.renderProducts();
            this.updateProductCount();
            
            form.reset();
            this.hideEmptyState();
            this.showAlert('Product added successfully!', 'success');
            
            // Scroll to top to show the new product
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
        } catch (error) {
            this.showAlert('Error adding product: ' + error.message, 'error');
        } finally {
            const addButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(addButton, false);
        }
    }

    async updateProduct() {
        const form = document.getElementById('edit-product-form');
        const formData = new FormData(form);
        const productId = document.getElementById('edit-product-id').value;
        
        const productData = {
            name: formData.get('name').trim(),
            price: parseFloat(formData.get('price')),
            quantity: parseInt(formData.get('quantity'))
        };

        // Client-side validation
        if (!this.validateProduct(productData)) {
            return;
        }

        try {
            const updateButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(updateButton, true);

            const updatedProduct = await this.apiRequest(`${this.apiBaseUrl}/${productId}`, {
                method: 'PUT',
                body: JSON.stringify(productData)
            });

            // Update product in local array
            const index = this.products.findIndex(p => p.id == productId);
            if (index !== -1) {
                this.products[index] = updatedProduct;
                this.filteredProducts = [...this.products];
                this.renderProducts();
            }

            this.closeEditModal();
            this.showAlert('Product updated successfully!', 'success');
            
        } catch (error) {
            this.showAlert('Error updating product: ' + error.message, 'error');
        } finally {
            const updateButton = form.querySelector('button[type="submit"]');
            this.setButtonLoading(updateButton, false);
        }
    }

    async deleteProduct(productId, productName) {
        try {
            const deleteButton = document.getElementById('confirm-delete-btn');
            this.setButtonLoading(deleteButton, true);

            await this.apiRequest(`${this.apiBaseUrl}/${productId}`, {
                method: 'DELETE'
            });

            // Remove product from local array
            this.products = this.products.filter(p => p.id != productId);
            this.filteredProducts = this.filteredProducts.filter(p => p.id != productId);
            
            this.renderProducts();
            this.updateProductCount();
            
            if (this.products.length === 0) {
                this.showEmptyState();
            }

            this.closeDeleteModal();
            this.showAlert(`Product "${productName}" deleted successfully!`, 'success');
            
        } catch (error) {
            this.showAlert('Error deleting product: ' + error.message, 'error');
        } finally {
            const deleteButton = document.getElementById('confirm-delete-btn');
            this.setButtonLoading(deleteButton, false);
        }
    }

    // UI Methods
    renderProducts() {
        const grid = document.getElementById('products-grid');
        
        if (this.filteredProducts.length === 0) {
            grid.innerHTML = '';
            return;
        }

        grid.innerHTML = this.filteredProducts.map(product => `
            <div class="product-card fade-in">
                <h3>${this.escapeHtml(product.name)}</h3>
                <div class="product-details">
                    <div class="product-detail">
                        <label><i class="fas fa-hashtag"></i> ID:</label>
                        <span>${product.id}</span>
                    </div>
                    <div class="product-detail">
                        <label><i class="fas fa-dollar-sign"></i> Price:</label>
                        <span class="price">$${parseFloat(product.price).toFixed(2)}</span>
                    </div>
                    <div class="product-detail">
                        <label><i class="fas fa-cubes"></i> Quantity:</label>
                        <span class="quantity">${product.quantity}</span>
                    </div>
                </div>
                <div class="product-actions">
                    <button class="btn btn-edit" onclick="productManager.openEditModal('${product.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-delete" onclick="productManager.openDeleteModal('${product.id}', '${this.escapeHtml(product.name)}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterProducts() {
        const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
        
        if (searchTerm === '') {
            this.filteredProducts = [...this.products];
        } else {
            this.filteredProducts = this.products.filter(product =>
                product.name.toLowerCase().includes(searchTerm)
            );
        }
        
        this.renderProducts();
        this.updateProductCount();
        
        if (this.filteredProducts.length === 0 && searchTerm !== '') {
            this.showEmptyState('No products found matching your search.');
        } else if (this.products.length === 0) {
            this.showEmptyState();
        } else {
            this.hideEmptyState();
        }
    }

    // Modal Methods
    openEditModal(productId) {
        const product = this.products.find(p => p.id == productId);
        if (!product) return;

        document.getElementById('edit-product-id').value = product.id;
        document.getElementById('edit-product-name').value = product.name;
        document.getElementById('edit-product-price').value = product.price;
        document.getElementById('edit-product-quantity').value = product.quantity;

        document.getElementById('edit-modal').style.display = 'flex';
        document.getElementById('edit-product-name').focus();
    }

    closeEditModal() {
        document.getElementById('edit-modal').style.display = 'none';
        document.getElementById('edit-product-form').reset();
    }

    openDeleteModal(productId, productName) {
        const product = this.products.find(p => p.id == productId);
        if (!product) return;

        document.getElementById('delete-product-name').textContent = productName;
        document.getElementById('delete-product-details').textContent = 
            `Price: $${parseFloat(product.price).toFixed(2)} | Quantity: ${product.quantity}`;

        // Set up delete confirmation
        const confirmButton = document.getElementById('confirm-delete-btn');
        confirmButton.onclick = () => this.deleteProduct(productId, productName);

        document.getElementById('delete-modal').style.display = 'flex';
    }

    closeDeleteModal() {
        document.getElementById('delete-modal').style.display = 'none';
    }

    closeAllModals() {
        this.closeEditModal();
        this.closeDeleteModal();
    }

    // Utility Methods
    validateProduct(product) {
        const errors = [];

        if (!product.name || product.name.length === 0) {
            errors.push('Product name is required');
        } else if (product.name.length > 100) {
            errors.push('Product name must be 100 characters or less');
        }

        if (isNaN(product.price) || product.price < 0) {
            errors.push('Price must be a valid positive number');
        }

        if (!Number.isInteger(product.quantity) || product.quantity < 0) {
            errors.push('Quantity must be a valid positive integer');
        }

        if (errors.length > 0) {
            this.showAlert('Validation errors:\\n• ' + errors.join('\\n• '), 'error');
            return false;
        }

        return true;
    }

    showAlert(message, type = 'success') {
        const alert = document.getElementById('alert');
        const alertMessage = document.getElementById('alert-message');
        
        alert.className = `alert ${type}`;
        alertMessage.textContent = message;
        alert.style.display = 'flex';
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.closeAlert();
            }, 5000);
        }

        // Scroll to top to show alert
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    closeAlert() {
        document.getElementById('alert').style.display = 'none';
    }

    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
        document.getElementById('refresh-btn').disabled = show;
        
        if (show) {
            document.getElementById('refresh-btn').innerHTML = 
                '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            document.getElementById('refresh-btn').innerHTML = 
                '<i class="fas fa-sync-alt"></i> Refresh';
        }
    }

    showEmptyState(customMessage = null) {
        const emptyState = document.getElementById('empty-state');
        const defaultMessage = emptyState.querySelector('p');
        
        if (customMessage) {
            defaultMessage.textContent = customMessage;
        } else {
            defaultMessage.textContent = 'Start by adding your first product above.';
        }
        
        emptyState.style.display = 'block';
    }

    hideEmptyState() {
        document.getElementById('empty-state').style.display = 'none';
    }

    updateProductCount() {
        const count = this.filteredProducts.length;
        const total = this.products.length;
        const countElement = document.getElementById('product-count');
        
        if (count === total) {
            countElement.textContent = `${count} product${count !== 1 ? 's' : ''}`;
        } else {
            countElement.textContent = `${count} of ${total} product${total !== 1 ? 's' : ''}`;
        }
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for HTML onclick events
function loadProducts() {
    productManager.loadProducts();
}

function filterProducts() {
    productManager.filterProducts();
}

function closeAlert() {
    productManager.closeAlert();
}

function closeEditModal() {
    productManager.closeEditModal();
}

function closeDeleteModal() {
    productManager.closeDeleteModal();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.productManager = new ProductManager();
});

// Handle page refresh with unsaved changes
window.addEventListener('beforeunload', (e) => {
    const forms = document.querySelectorAll('form');
    let hasUnsavedChanges = false;
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[type="text"], input[type="number"]');
        inputs.forEach(input => {
            if (input.value.trim() !== '' && input.defaultValue !== input.value) {
                hasUnsavedChanges = true;
            }
        });
    });
    
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Service Worker Registration (for future PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment when you want to add service worker
        // navigator.serviceWorker.register('/service-worker.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(registrationError => console.log('SW registration failed'));
    });
}