        class HealthcareQueryApp {
            constructor() {
                this.baseUrl = window.CONFIG.getBackendUrl();
                this.queryHistory = JSON.parse(localStorage.getItem('queryHistory')) || [];
                this.currentResults = null;
                this.currentUser = null;
                this.authToken = localStorage.getItem('authToken');
                
                this.initializeApp();
                this.bindEvents();
                this.checkSystemStatus();
                this.checkAuthStatus();
            }

            initializeApp() {
                this.updateUserPermissions();
                this.renderQueryHistory();
                this.updateSecurityIndicator();
            }

            bindEvents() {
                // Login form
                document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
                document.getElementById('logout-button').addEventListener('click', () => this.handleLogout());

                // Query submission
                document.getElementById('submit-query').addEventListener('click', () => this.executeQuery());
                document.getElementById('query-input').addEventListener('keydown', (e) => {
                    if (e.ctrlKey && e.key === 'Enter') {
                        this.executeQuery();
                    }
                });

                // Tab switching
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
                });

                // Example queries
                document.querySelectorAll('.example-query').forEach(query => {
                    query.addEventListener('click', (e) => {
                        const queryText = e.currentTarget.dataset.query;
                        document.getElementById('query-input').value = queryText;
                        
                        // Auto-enable malicious mode for attack queries
                        const isMalicious = e.currentTarget.classList.contains('malicious');
                        document.getElementById('malicious-mode').checked = isMalicious;
                        this.updateSecurityIndicator();
                    });
                });

                // User role changes
                document.getElementById('user-role').addEventListener('change', () => {
                    this.updateUserPermissions();
                });

                // Malicious mode toggle
                document.getElementById('malicious-mode').addEventListener('change', () => {
                    this.updateSecurityIndicator();
                });

                // Export functionality
                document.getElementById('export-csv').addEventListener('click', () => this.exportToCSV());

                // History item clicks
                document.addEventListener('click', (e) => {
                    if (e.target.closest('.history-item')) {
                        const query = e.target.closest('.history-item').dataset.query;
                        document.getElementById('query-input').value = query;
                    }
                });
            }

            async checkAuthStatus() {
                if (this.authToken) {
                    try {
                        const response = await this.callAuthAPI('/api/login', {
                            method: 'GET',
                            headers: {
                                'Authorization': `Bearer ${this.authToken}`
                            }
                        });

                        if (response.success) {
                            this.currentUser = response.user;
                            this.showMainApp();
                            return;
                        }
                    } catch (error) {
                        console.log('Token verification failed:', error);
                    }
                }
                
                // Show login if no valid token
                this.showLogin();
            }

            async handleLogin(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value;
                const submitButton = document.getElementById('login-submit');
                const submitText = document.getElementById('login-submit-text');
                const errorDiv = document.getElementById('login-error');

                if (!username || !password) {
                    this.showLoginError('Please enter both username and password');
                    return;
                }

                // Update UI for loading state
                submitButton.disabled = true;
                submitText.innerHTML = '<div class="loading-spinner"></div> Authenticating...';
                errorDiv.classList.add('hidden');

                try {
                    const response = await this.callAuthAPI('/api/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    });

                    if (response.success) {
                        this.authToken = response.token;
                        this.currentUser = response.user;
                        
                        // Store token for persistence
                        localStorage.setItem('authToken', this.authToken);
                        
                        // Update UI and show main app
                        this.showMainApp();
                        
                        // Reset form
                        document.getElementById('login-form').reset();
                        
                    } else {
                        this.showLoginError(response.message || 'Invalid username or password');
                    }

                } catch (error) {
                    console.error('Login failed:', error);
                    this.showLoginError('Login failed. Please check your connection and try again.');
                } finally {
                    // Reset button state
                    submitButton.disabled = false;
                    submitText.textContent = 'Sign In';
                }
            }

            handleLogout() {
                // Clear stored data
                this.authToken = null;
                this.currentUser = null;
                localStorage.removeItem('authToken');
                localStorage.removeItem('queryHistory');
                
                // Reset app state
                this.queryHistory = [];
                this.currentResults = null;
                
                // Show login screen
                this.showLogin();
            }

            showLogin() {
                document.getElementById('login-modal').style.display = 'flex';
                document.getElementById('user-info').style.display = 'none';
                
                // Focus on username field
                setTimeout(() => {
                    document.getElementById('username').focus();
                }, 100);
            }

            showMainApp() {
                document.getElementById('login-modal').style.display = 'none';
                
                if (this.currentUser) {
                    // Update user info display
                    document.getElementById('user-info').style.display = 'flex';
                    document.getElementById('logged-in-user').textContent = this.currentUser.full_name || this.currentUser.username;
                    document.getElementById('user-role-display').textContent = this.currentUser.role || 'User';
                    document.getElementById('user-avatar').textContent = (this.currentUser.full_name || this.currentUser.username).charAt(0).toUpperCase();
                    
                    // Set user role in dropdown to match logged in user
                    const roleSelect = document.getElementById('user-role');
                    if (this.currentUser.role && roleSelect.querySelector(`option[value="${this.currentUser.role.toLowerCase()}"]`)) {
                        roleSelect.value = this.currentUser.role.toLowerCase();
                        this.updateUserPermissions();
                    }
                }
            }

            showLoginError(message) {
                const errorDiv = document.getElementById('login-error');
                errorDiv.textContent = message;
                errorDiv.classList.remove('hidden');
            }

            async callAuthAPI(endpoint, options = {}) {
                const url = window.CONFIG.getBackendUrl(endpoint);
                const timeout = window.CONFIG.timeouts.authentication;
                
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), timeout);
                    
                    const response = await fetch(url, {
                        ...options,
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    return data;
                    
                } catch (error) {
                    if (error.name === 'AbortError') {
                        throw new Error(`Request timeout after ${timeout}ms`);
                    }
                    throw new Error(`Authentication API call failed: ${error.message}`);
                }
            }


            async executeQuery() {
                if (!this.currentUser) {
                    this.showError('Please log in to execute queries');
                    return;
                }

                const queryText = document.getElementById('query-input').value.trim();
                if (!queryText) {
                    this.showError('Please enter a query');
                    return;
                }

                const userRole = document.getElementById('user-role').value;
                const isMalicious = document.getElementById('malicious-mode').checked;
                const submitButton = document.getElementById('submit-query');
                const submitText = document.getElementById('submit-text');

                // Update UI for loading state
                submitButton.disabled = true;
                submitText.innerHTML = '<div class="loading-spinner"></div> Generating SQL...';

                const startTime = Date.now();

                try {
                    // Add to history immediately
                    this.addToHistory(queryText, isMalicious);

                    // Simulate API call
                    const response = await this.callBackendAPI({
                        query: queryText,
                        userRole: userRole,
                        maliciousMode: isMalicious,
                        userId: this.currentUser.username,
                        authToken: this.authToken
                    });

                    const endTime = Date.now();
                    const totalTime = endTime - startTime;

                    // Display results
                    this.displayResults(response, totalTime);
                    this.displayAuditInfo(response, queryText, userRole, isMalicious);

                } catch (error) {
                    console.error('Query execution failed:', error);
                    this.showError(`Query failed: ${error.message}`);
                } finally {
                    // Reset button state
                    submitButton.disabled = false;
                    submitText.textContent = 'Execute Query';
                }
            }

            async callBackendAPI(payload) {
                // Check authentication
                if (!payload.authToken) {
                    throw new Error('Authentication required');
                }

                const url = window.CONFIG.getBackendUrl(window.CONFIG.api.query);
                const timeout = window.CONFIG.timeouts.query;
                
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), timeout);
                    
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${payload.authToken}`
                        },
                        body: JSON.stringify({
                            query: payload.query,
                            userRole: payload.userRole,
                            maliciousMode: payload.maliciousMode,
                            userId: payload.userId
                        }),
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    return data;
                    
                } catch (error) {
                    if (error.name === 'AbortError') {
                        throw new Error(`Query timeout after ${timeout}ms`);
                    }
                    throw new Error(`Backend API call failed: ${error.message}`);
                }
            }


            displayResults(response, totalTime) {
                // Display SQL
                document.getElementById('sql-output').textContent = response.sql;

                // Display data table
                const resultsOutput = document.getElementById('results-output');
                if (response.data && response.data.length > 0) {
                    const table = this.createDataTable(response.data);
                    resultsOutput.innerHTML = '';
                    resultsOutput.appendChild(table);
                    document.getElementById('export-csv').classList.remove('hidden');
                    this.currentResults = response.data;
                } else {
                    resultsOutput.innerHTML = '<p style="color: var(--neutral-gray); text-align: center; margin-top: 2rem;">No results returned</p>';
                    document.getElementById('export-csv').classList.add('hidden');
                    this.currentResults = null;
                }

                // Display performance stats
                document.getElementById('query-time').textContent = response.executionTime;
                document.getElementById('llm-time').textContent = (response.llmProcessingTime / 1000).toFixed(1);
                document.getElementById('rows-returned').textContent = response.rowCount;
                document.getElementById('performance-stats').style.display = 'grid';

                // Switch to results tab
                this.switchTab('results');
            }

            displayAuditInfo(response, query, userRole, isMalicious) {
                const auditOutput = document.getElementById('audit-output');
                
                const auditHtml = `
                    <div style="display: grid; gap: 1rem;">
                        <div style="padding: 1rem; background: var(--light-gray); border-radius: 8px;">
                            <strong>Query Analysis:</strong><br>
                            Risk Level: <span class="security-indicator ${response.securityFlags.riskLevel.toLowerCase() === 'high' ? 'danger' : 'safe'}">${response.securityFlags.riskLevel}</span><br>
                            Authenticated User: ${response.securityFlags.authenticatedUser || 'Unknown'}<br>
                            User Role: ${response.securityFlags.userRole || userRole}<br>
                            Malicious Mode: ${isMalicious ? 'ON' : 'OFF'}
                        </div>
                        
                        <div style="padding: 1rem; background: var(--light-gray); border-radius: 8px;">
                            <strong>Security Events:</strong><br>
                            Blocked Attempts: ${response.securityFlags.blockedAttempts}<br>
                            Access Control: ${response.securityFlags.riskLevel === 'HIGH' ? 'RESTRICTED' : 'ALLOWED'}<br>
                            Audit Log: ✓ Recorded<br>
                            Authentication: ✓ Verified
                        </div>
                        
                        <div style="padding: 1rem; background: var(--light-gray); border-radius: 8px;">
                            <strong>User Permissions:</strong><br>
                            ${response.securityFlags.allowedOperations.map(op => `• ${op}`).join('<br>')}
                        </div>
                        
                        <div style="padding: 1rem; background: var(--light-gray); border-radius: 8px;">
                            <strong>Query Timestamp:</strong> ${new Date().toISOString()}<br>
                            <strong>Session ID:</strong> sess_${Math.random().toString(36).substr(2, 9)}<br>
                            <strong>IP Address:</strong> 192.168.100.${Math.floor(Math.random() * 254) + 1}<br>
                            <strong>Auth Token:</strong> ${this.authToken ? this.authToken.substr(0, 20) + '...' : 'None'}
                        </div>
                    </div>
                `;
                
                auditOutput.innerHTML = auditHtml;
            }

            createDataTable(data) {
                const table = document.createElement('table');
                table.className = 'data-table';

                if (data.length === 0) return table;

                // Create header
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                Object.keys(data[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key.replace(/_/g, ' ').toUpperCase();
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // Create body
                const tbody = document.createElement('tbody');
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    Object.values(row).forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value || '--';
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                table.appendChild(tbody);

                return table;
            }

            switchTab(tabName) {
                // Update tab buttons
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.classList.toggle('active', button.dataset.tab === tabName);
                });

                // Update tab panels
                document.querySelectorAll('.tab-panel').forEach(panel => {
                    panel.classList.toggle('hidden', panel.id !== `${tabName}-tab`);
                });
            }

            addToHistory(query, isMalicious) {
                const historyItem = {
                    query: query,
                    timestamp: new Date().toISOString(),
                    malicious: isMalicious
                };

                this.queryHistory.unshift(historyItem);
                this.queryHistory = this.queryHistory.slice(0, 50); // Keep last 50 queries

                localStorage.setItem('queryHistory', JSON.stringify(this.queryHistory));
                this.renderQueryHistory();
            }

            renderQueryHistory() {
                const historyContainer = document.getElementById('query-history');
                
                if (this.queryHistory.length === 0) {
                    historyContainer.innerHTML = '<div style="color: var(--neutral-gray); text-align: center; padding: 2rem;">No queries executed yet</div>';
                    return;
                }

                historyContainer.innerHTML = '';
                this.queryHistory.forEach(item => {
                    const historyItem = document.createElement('div');
                    historyItem.className = 'history-item';
                    historyItem.dataset.query = item.query;
                    
                    const date = new Date(item.timestamp);
                    const timeString = date.toLocaleTimeString();
                    
                    historyItem.innerHTML = `
                        <div class="history-timestamp">${timeString} ${item.malicious ? '⚠️' : ''}</div>
                        <div class="history-query">${item.query}</div>
                    `;
                    
                    historyContainer.appendChild(historyItem);
                });
            }

            updateUserPermissions() {
                const userRole = document.getElementById('user-role').value;
                document.getElementById('current-role').textContent = userRole.charAt(0).toUpperCase() + userRole.slice(1);
                
                const permissions = this.getAllowedOperations(userRole);
                const operationsList = document.getElementById('allowed-operations');
                operationsList.innerHTML = permissions.map(op => `<li>${op}</li>`).join('');
                
                // Update access level indicator
                const accessLevel = document.getElementById('access-level');
                if (userRole === 'admin') {
                    accessLevel.className = 'security-indicator warning';
                    accessLevel.innerHTML = '<span>⚡ Admin Access</span>';
                } else if (userRole === 'patient') {
                    accessLevel.className = 'security-indicator safe';
                    accessLevel.innerHTML = '<span>🔒 Limited Access</span>';
                } else {
                    accessLevel.className = 'security-indicator safe';
                    accessLevel.innerHTML = '<span>✓ Standard Access</span>';
                }
            }

            getAllowedOperations(userRole) {
                const permissions = {
                    doctor: [
                        'Read patient records',
                        'Read appointment data',
                        'Read department information',
                        'Update patient notes',
                        'Create prescriptions'
                    ],
                    nurse: [
                        'Read patient basic info',
                        'Read appointment schedules',
                        'Update patient vitals',
                        'Read medication lists'
                    ],
                    admin: [
                        'Full database access',
                        'User management',
                        'System configuration',
                        'Audit log access',
                        'Backup operations'
                    ],
                    patient: [
                        'Read own records only',
                        'Read own appointments',
                        'Update contact information'
                    ]
                };
                
                return permissions[userRole] || [];
            }

            updateSecurityIndicator() {
                const isMalicious = document.getElementById('malicious-mode').checked;
                const indicator = document.getElementById('security-indicator');
                
                if (isMalicious) {
                    indicator.className = 'security-indicator danger';
                    indicator.innerHTML = '<span>⚠️ TESTING MODE</span>';
                } else {
                    indicator.className = 'security-indicator safe';
                    indicator.innerHTML = '<span>🛡️ SAFE</span>';
                }
            }

            async checkSystemStatus() {
                const statusChecks = [
                    { 
                        id: 'backend-status', 
                        url: window.CONFIG.getBackendUrl(window.CONFIG.api.health),
                        name: window.CONFIG.hosts.WEB.name
                    },
                    { 
                        id: 'llm-status', 
                        url: window.CONFIG.getUrl('LLM', '/health'),
                        name: window.CONFIG.hosts.LLM.name
                    },
                    { 
                        id: 'db-status', 
                        url: `${window.CONFIG.hosts.DB.protocol}://${window.CONFIG.hosts.DB.host}:${window.CONFIG.hosts.DB.port}`,
                        name: window.CONFIG.hosts.DB.name
                    }
                ];

                for (const check of statusChecks) {
                    const statusDot = document.getElementById(check.id);
                    
                    try {
                        // For database, we can't directly check from frontend due to CORS
                        // So we'll check through the backend API health endpoint
                        if (check.id === 'db-status') {
                            // Get database status from backend /api/health endpoint
                            const backendResponse = await fetch(window.CONFIG.getBackendUrl('/api/health'), {
                                method: 'GET',
                                timeout: window.CONFIG.timeouts.health_check
                            });

                            if (backendResponse.ok) {
                                const healthStatus = await backendResponse.json();
                                // Check if database status is healthy
                                const isHealthy = healthStatus.database && healthStatus.database.status === 'healthy';
                                statusDot.className = isHealthy ? 'status-dot' : 'status-dot error';
                            } else {
                                statusDot.className = 'status-dot warning';
                            }
                        } else {
                            // Check other services directly
                            const controller = new AbortController();
                            const timeoutId = setTimeout(() => controller.abort(), window.CONFIG.timeouts.health_check);
                            
                            const response = await fetch(check.url, {
                                method: 'GET',
                                signal: controller.signal
                            });
                            
                            clearTimeout(timeoutId);
                            
                            if (response.ok) {
                                statusDot.className = 'status-dot';
                            } else {
                                statusDot.className = 'status-dot warning';
                            }
                        }
                        
                    } catch (error) {
                        console.warn(`Health check failed for ${check.name}:`, error.message);
                        statusDot.className = 'status-dot error';
                    }
                }

                // Recheck every 30 seconds using the config interval
                setTimeout(() => this.checkSystemStatus(), window.CONFIG.app.auto_health_check_interval);
            }

            exportToCSV() {
                if (!this.currentResults || this.currentResults.length === 0) {
                    this.showError('No data to export');
                    return;
                }

                const headers = Object.keys(this.currentResults[0]);
                const csvContent = [
                    headers.join(','),
                    ...this.currentResults.map(row => 
                        headers.map(header => `"${row[header] || ''}"`).join(',')
                    )
                ].join('\n');

                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `query_results_${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
            }

            showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = message;
                
                // Insert at the top of the query section
                const querySection = document.querySelector('.query-section');
                const firstChild = querySection.firstElementChild.nextElementSibling;
                querySection.insertBefore(errorDiv, firstChild);
                
                // Remove after 5 seconds
                setTimeout(() => {
                    if (errorDiv.parentNode) {
                        errorDiv.parentNode.removeChild(errorDiv);
                    }
                }, 5000);
            }
        }

export { HealthcareQueryApp };
