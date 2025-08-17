// Smart Receipt Upload Component
// Drag-drop or camera capture with AI processing

class SmartReceiptUpload {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentReceipt = null;
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
        this.injectStyles();
    }

    render() {
        const html = `
            <div class="receipt-upload-container">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2L12 14M12 14L16 10M12 14L8 10"/>
                            <path d="M20 13V18C20 19.1 19.1 20 18 20H6C4.9 20 4 19.1 4 18V13"/>
                        </svg>
                    </div>
                    <div class="upload-text">
                        <p class="primary">Drop receipt here or click to upload</p>
                        <p class="secondary">Take a photo • Upload image • PDF</p>
                    </div>
                    <input type="file" id="receiptInput" accept="image/*,application/pdf" hidden>
                    
                    <!-- Camera button for mobile -->
                    <button class="camera-btn" id="cameraBtn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                            <circle cx="12" cy="13" r="4"/>
                        </svg>
                        <span>Camera</span>
                    </button>
                </div>

                <!-- Processing overlay -->
                <div class="processing-overlay" id="processingOverlay" style="display: none;">
                    <div class="processing-content">
                        <div class="ai-scanner">
                            <div class="scan-line"></div>
                        </div>
                        <p class="processing-text">AI is reading your receipt...</p>
                        <div class="processing-steps">
                            <div class="step active">Extracting text</div>
                            <div class="step">Finding vendor</div>
                            <div class="step">Analyzing prices</div>
                            <div class="step">Checking for savings</div>
                        </div>
                    </div>
                </div>

                <!-- Results view -->
                <div class="receipt-results" id="receiptResults" style="display: none;">
                    <div class="receipt-preview">
                        <img id="receiptImage" src="" alt="Receipt">
                        <button class="retake-btn" onclick="smartReceipt.reset()">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M1 4v6h6M23 20v-6h-6"/>
                                <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                            </svg>
                            Retake
                        </button>
                    </div>
                    
                    <div class="receipt-data">
                        <div class="confidence-badge">
                            <span class="confidence-score"></span>
                            <span class="confidence-label">Confidence</span>
                        </div>
                        
                        <div class="receipt-field">
                            <label>Vendor</label>
                            <input type="text" id="vendorName" class="editable-field">
                        </div>
                        
                        <div class="receipt-field">
                            <label>Amount</label>
                            <input type="text" id="totalAmount" class="editable-field amount">
                        </div>
                        
                        <div class="receipt-field">
                            <label>Date</label>
                            <input type="date" id="receiptDate" class="editable-field">
                        </div>
                        
                        <div class="receipt-field">
                            <label>Category</label>
                            <select id="category" class="editable-field">
                                <option value="materials">Materials</option>
                                <option value="tools">Tools</option>
                                <option value="vehicle">Vehicle</option>
                                <option value="safety">Safety</option>
                                <option value="office">Office</option>
                                <option value="subcontractor">Subcontractor</option>
                            </select>
                        </div>

                        <!-- AI Insights -->
                        <div class="ai-insights" id="aiInsights">
                            <!-- Populated dynamically -->
                        </div>

                        <div class="action-buttons">
                            <button class="save-btn primary" onclick="smartReceipt.saveExpense()">
                                Save Expense
                            </button>
                            <button class="save-btn secondary" onclick="smartReceipt.saveAndAnother()">
                                Save & Add Another
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Recent receipts -->
                <div class="recent-receipts" id="recentReceipts">
                    <h3>Recent Uploads</h3>
                    <div class="receipt-list">
                        <!-- Populated dynamically -->
                    </div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }

    injectStyles() {
        const styles = `
            <style>
                .receipt-upload-container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .upload-area {
                    border: 2px dashed rgba(255, 152, 0, 0.3);
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                    background: rgba(255, 152, 0, 0.05);
                    transition: all 0.3s;
                    position: relative;
                    cursor: pointer;
                }

                .upload-area.dragover {
                    border-color: #FF9800;
                    background: rgba(255, 152, 0, 0.1);
                    transform: scale(1.02);
                }

                .upload-icon svg {
                    width: 48px;
                    height: 48px;
                    color: #FF9800;
                    margin-bottom: 16px;
                }

                .upload-text .primary {
                    font-size: 18px;
                    font-weight: 600;
                    color: #fff;
                    margin-bottom: 8px;
                }

                .upload-text .secondary {
                    font-size: 14px;
                    color: #999;
                }

                .camera-btn {
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    background: #FF9800;
                    color: #000;
                    border: none;
                    border-radius: 25px;
                    padding: 10px 20px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-weight: 500;
                    cursor: pointer;
                }

                .camera-btn svg {
                    width: 20px;
                    height: 20px;
                }

                .processing-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.9);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .processing-content {
                    text-align: center;
                    max-width: 400px;
                }

                .ai-scanner {
                    width: 200px;
                    height: 200px;
                    border: 2px solid #FF9800;
                    border-radius: 16px;
                    margin: 0 auto 30px;
                    position: relative;
                    overflow: hidden;
                }

                .scan-line {
                    position: absolute;
                    width: 100%;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #FF9800, transparent);
                    animation: scan 2s linear infinite;
                }

                @keyframes scan {
                    0% { top: 0; }
                    100% { top: 100%; }
                }

                .processing-text {
                    font-size: 20px;
                    color: #fff;
                    margin-bottom: 20px;
                }

                .processing-steps {
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                    flex-wrap: wrap;
                }

                .step {
                    padding: 6px 16px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    font-size: 12px;
                    color: #666;
                    transition: all 0.3s;
                }

                .step.active {
                    background: rgba(255, 152, 0, 0.2);
                    color: #FF9800;
                }

                .receipt-results {
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    gap: 30px;
                    margin-top: 30px;
                }

                .receipt-preview {
                    position: relative;
                }

                .receipt-preview img {
                    width: 100%;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                }

                .retake-btn {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(0, 0, 0, 0.7);
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 12px;
                    cursor: pointer;
                }

                .retake-btn svg {
                    width: 16px;
                    height: 16px;
                }

                .receipt-data {
                    background: #1a1a1a;
                    border-radius: 16px;
                    padding: 24px;
                }

                .confidence-badge {
                    display: inline-flex;
                    flex-direction: column;
                    align-items: center;
                    background: rgba(255, 152, 0, 0.1);
                    border: 1px solid rgba(255, 152, 0, 0.3);
                    border-radius: 12px;
                    padding: 12px 20px;
                    margin-bottom: 20px;
                }

                .confidence-score {
                    font-size: 24px;
                    font-weight: 700;
                    color: #FF9800;
                }

                .confidence-label {
                    font-size: 12px;
                    color: #999;
                }

                .receipt-field {
                    margin-bottom: 16px;
                }

                .receipt-field label {
                    display: block;
                    font-size: 12px;
                    color: #999;
                    margin-bottom: 6px;
                    text-transform: uppercase;
                }

                .editable-field {
                    width: 100%;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 12px;
                    color: #fff;
                    font-size: 16px;
                }

                .editable-field:focus {
                    border-color: #FF9800;
                    outline: none;
                }

                .editable-field.amount {
                    font-size: 20px;
                    font-weight: 600;
                }

                .ai-insights {
                    margin: 20px 0;
                    padding: 16px;
                    background: rgba(255, 152, 0, 0.05);
                    border: 1px solid rgba(255, 152, 0, 0.2);
                    border-radius: 12px;
                }

                .insight-item {
                    display: flex;
                    align-items: start;
                    gap: 8px;
                    margin-bottom: 8px;
                }

                .insight-item:last-child {
                    margin-bottom: 0;
                }

                .insight-icon {
                    font-size: 16px;
                    margin-top: 2px;
                }

                .insight-text {
                    flex: 1;
                    font-size: 14px;
                    color: #fff;
                    line-height: 1.5;
                }

                .warning {
                    color: #ff5252;
                }

                .action-buttons {
                    display: flex;
                    gap: 12px;
                    margin-top: 24px;
                }

                .save-btn {
                    flex: 1;
                    padding: 14px;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .save-btn.primary {
                    background: #FF9800;
                    color: #000;
                }

                .save-btn.secondary {
                    background: transparent;
                    color: #FF9800;
                    border: 1px solid #FF9800;
                }

                .recent-receipts {
                    margin-top: 40px;
                }

                .recent-receipts h3 {
                    color: #999;
                    font-size: 14px;
                    text-transform: uppercase;
                    margin-bottom: 16px;
                }

                .receipt-list {
                    display: grid;
                    gap: 12px;
                }

                .receipt-item {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    background: #1a1a1a;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .receipt-item:hover {
                    border-color: #FF9800;
                }

                .receipt-thumb {
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    overflow: hidden;
                }

                .receipt-thumb img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }

                .receipt-info {
                    flex: 1;
                }

                .receipt-vendor {
                    font-weight: 600;
                    color: #fff;
                }

                .receipt-meta {
                    font-size: 12px;
                    color: #999;
                }

                .receipt-amount {
                    font-size: 18px;
                    font-weight: 700;
                    color: #FF9800;
                }

                @media (max-width: 768px) {
                    .receipt-results {
                        grid-template-columns: 1fr;
                    }
                    
                    .receipt-preview img {
                        max-height: 300px;
                        object-fit: contain;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('receiptInput');
        const cameraBtn = document.getElementById('cameraBtn');

        // Click to upload
        uploadArea.addEventListener('click', (e) => {
            if (e.target !== cameraBtn && !cameraBtn.contains(e.target)) {
                fileInput.click();
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.processFile(file);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                this.processFile(file);
            }
        });

        // Camera button (mobile)
        cameraBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.setAttribute('capture', 'environment');
            fileInput.click();
        });

        // Load recent receipts
        this.loadRecentReceipts();
    }

    async processFile(file) {
        if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
            alert('Please upload an image or PDF file');
            return;
        }

        // Show processing overlay
        document.getElementById('processingOverlay').style.display = 'flex';
        this.animateProcessingSteps();

        // Convert to base64
        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Data = e.target.result;
            
            // Show preview immediately
            if (file.type.startsWith('image/')) {
                document.getElementById('receiptImage').src = base64Data;
            }

            // Send to backend for AI processing
            try {
                const response = await fetch('/api/receipts/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                    },
                    body: JSON.stringify({
                        image_data: base64Data,
                        file_type: file.type
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.displayResults(data);
                } else {
                    // Fallback to mock data for demo
                    this.displayResults(this.getMockReceiptData());
                }
            } catch (error) {
                // console.error('Error processing receipt:', error);
                this.displayResults(this.getMockReceiptData());
            }
        };

        reader.readAsDataURL(file);
    }

    animateProcessingSteps() {
        const steps = document.querySelectorAll('.step');
        let currentStep = 0;

        const interval = setInterval(() => {
            steps.forEach(step => step.classList.remove('active'));
            steps[currentStep].classList.add('active');
            
            currentStep++;
            if (currentStep >= steps.length) {
                clearInterval(interval);
            }
        }, 800);
    }

    displayResults(data) {
        // Hide processing overlay
        document.getElementById('processingOverlay').style.display = 'none';
        
        // Show results
        document.getElementById('receiptResults').style.display = 'grid';
        
        // Populate fields
        document.getElementById('vendorName').value = data.vendor_name || '';
        document.getElementById('totalAmount').value = `$${data.total_amount?.toFixed(2) || '0.00'}`;
        document.getElementById('receiptDate').value = data.date?.split('T')[0] || new Date().toISOString().split('T')[0];
        document.getElementById('category').value = data.category || 'materials';
        
        // Show confidence
        document.querySelector('.confidence-score').textContent = `${Math.round((data.confidence_score || 0.85) * 100)}%`;
        
        // Display AI insights
        this.displayInsights(data.insights || [], data.warnings || []);
        
        // Store current receipt data
        this.currentReceipt = data;
    }

    displayInsights(insights, warnings) {
        const container = document.getElementById('aiInsights');
        let html = '';
        
        // Display insights
        insights.forEach(insight => {
            html += `
                <div class="insight-item">
                    <span class="insight-icon">💡</span>
                    <span class="insight-text">${insight}</span>
                </div>
            `;
        });
        
        // Display warnings
        warnings.forEach(warning => {
            html += `
                <div class="insight-item warning">
                    <span class="insight-icon">⚠️</span>
                    <span class="insight-text">${warning}</span>
                </div>
            `;
        });
        
        container.innerHTML = html || '<p style="color: #999; text-align: center;">No special insights for this receipt</p>';
    }

    async saveExpense() {
        const expenseData = {
            vendor_name: document.getElementById('vendorName').value,
            amount: parseFloat(document.getElementById('totalAmount').value.replace('$', '')),
            date: document.getElementById('receiptDate').value,
            category: document.getElementById('category').value,
            receipt_data: this.currentReceipt
        };

        try {
            const response = await fetch('/api/expenses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(expenseData)
            });

            if (response.ok) {
                this.showSuccess('Expense saved successfully!');
                this.addToRecentReceipts(expenseData);
                setTimeout(() => this.reset(), 2000);
            }
        } catch (error) {
            // console.error('Error saving expense:', error);
            alert('Error saving expense. Please try again.');
        }
    }

    saveAndAnother() {
        this.saveExpense();
        // Reset will be called after save completes
    }

    reset() {
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('receiptResults').style.display = 'none';
        document.getElementById('receiptInput').value = '';
        this.currentReceipt = null;
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00c853;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-weight: 600;
            z-index: 2000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(successDiv);
        setTimeout(() => successDiv.remove(), 3000);
    }

    loadRecentReceipts() {
        // Would load from API
        const mockReceipts = [
            {
                id: 1,
                vendor: 'Home Depot',
                amount: 156.42,
                date: '2 hours ago',
                category: 'materials',
                thumbnail: '/static/images/receipt-thumb.jpg'
            },
            {
                id: 2,
                vendor: 'Harbor Freight',
                amount: 89.95,
                date: 'Yesterday',
                category: 'tools',
                thumbnail: '/static/images/receipt-thumb.jpg'
            }
        ];

        const container = document.querySelector('.receipt-list');
        container.innerHTML = mockReceipts.map(receipt => `
            <div class="receipt-item" onclick="smartReceipt.viewReceipt(${receipt.id})">
                <div class="receipt-thumb">
                    <img src="${receipt.thumbnail}" alt="Receipt">
                </div>
                <div class="receipt-info">
                    <div class="receipt-vendor">${receipt.vendor}</div>
                    <div class="receipt-meta">${receipt.date} • ${receipt.category}</div>
                </div>
                <div class="receipt-amount">$${receipt.amount.toFixed(2)}</div>
            </div>
        `).join('');
    }

    addToRecentReceipts(expense) {
        // Add to top of recent list
        const container = document.querySelector('.receipt-list');
        const newItem = document.createElement('div');
        newItem.className = 'receipt-item';
        newItem.innerHTML = `
            <div class="receipt-thumb">
                <img src="${document.getElementById('receiptImage').src}" alt="Receipt">
            </div>
            <div class="receipt-info">
                <div class="receipt-vendor">${expense.vendor_name}</div>
                <div class="receipt-meta">Just now • ${expense.category}</div>
            </div>
            <div class="receipt-amount">$${expense.amount.toFixed(2)}</div>
        `;
        
        container.insertBefore(newItem, container.firstChild);
    }

    viewReceipt(id) {
        // Would load and display receipt details
        // console.log('View receipt:', id);
    }

    getMockReceiptData() {
        return {
            vendor_name: 'Home Depot',
            total_amount: 156.42,
            date: new Date().toISOString(),
            category: 'materials',
            confidence_score: 0.92,
            insights: [
                'This purchase is 15% higher than your average at Home Depot',
                'You\'ve spent $1,250 on materials this month',
                'Tax deductible: Save this receipt for year-end filing'
            ],
            warnings: [
                'Similar purchase detected 3 days ago for $154.89'
            ],
            items: [
                { name: '2x4 Lumber', price: 45.60, category: 'materials' },
                { name: 'Wood Screws', price: 12.99, category: 'materials' },
                { name: 'Paint Primer', price: 34.95, category: 'materials' }
            ]
        };
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.smartReceipt = new SmartReceiptUpload('receiptUploadContainer');
    });
} else {
    if (document.getElementById('receiptUploadContainer')) {
        window.smartReceipt = new SmartReceiptUpload('receiptUploadContainer');
    }
}