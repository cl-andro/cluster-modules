/* 🚀 Cluster Registry Client Application (GitHub Pages Edition) */

document.addEventListener('DOMContentLoaded', () => {
    // State management
    let allPackages = {};
    let filteredPackages = [];
    let currentCategory = 'all';

    // DOM Elements
    const packagesGrid = document.getElementById('packages-grid');
    const searchInput = document.getElementById('search-input');
    const statTotalPackages = document.getElementById('stat-total-packages');
    const resultsCount = document.getElementById('results-count');
    
    // Filter Sidebar
    const filterButtons = document.querySelectorAll('.filter-item');

    // Modals
    const publishModal = document.getElementById('publish-modal');
    const detailsModal = document.getElementById('details-modal');
    
    // Open/Close buttons
    const openPublishModalBtn = document.getElementById('open-publish-modal-btn');
    const closePublishModalBtn = document.getElementById('close-publish-modal-btn');
    const closeDetailsModalBtn = document.getElementById('close-details-modal-btn');
    const goToGithubBtn = document.getElementById('go-to-github-btn');

    // Detail Modal Fields
    const detailsName = document.getElementById('details-name');
    const detailsVersion = document.getElementById('details-version');
    const detailsDesc = document.getElementById('details-desc');
    const detailsInstallCmd = document.getElementById('details-install-cmd');
    const detailsGitUrl = document.getElementById('details-git-url');
    const detailsLicense = document.getElementById('details-license');
    const detailsOutputPath = document.getElementById('details-output-path');

    // Copy Buttons
    const copyInstallBtn = document.getElementById('copy-install-btn');
    const copyDetailsInstallBtn = document.getElementById('copy-details-install-btn');

    // Initialize application
    fetchPackages();

    // Fetch catalog index from relative local JSON
    async function fetchPackages() {
        showLoadingState();
        try {
            const response = await fetch('./index.json');
            const data = await response.json();
            allPackages = data.packages || {};
            applyFilters();
            updateStats();
        } catch (error) {
            console.error('Failed to load packages index:', error);
            packagesGrid.innerHTML = `
                <div class="loading-spinner-wrapper">
                    <p class="error-text">❌ Failed to retrieve package catalog. Please verify that index.json exists.</p>
                </div>
            `;
        }
    }

    function showLoadingState() {
        packagesGrid.innerHTML = `
            <div class="loading-spinner-wrapper">
                <div class="spinner"></div>
                <p>Fetching package index...</p>
            </div>
        `;
    }

    function updateStats() {
        const count = Object.keys(allPackages).length;
        statTotalPackages.textContent = count;
    }

    // Apply category selection + search queries
    function applyFilters() {
        const query = searchInput.value.toLowerCase().trim();
        filteredPackages = [];

        Object.entries(allPackages).forEach(([name, pkg]) => {
            const matchesCategory = matchesActiveCategory(name, pkg);
            const matchesSearch = name.toLowerCase().includes(query) || 
                                  pkg.description.toLowerCase().includes(query) ||
                                  pkg.license.toLowerCase().includes(query);

            if (matchesCategory && matchesSearch) {
                filteredPackages.push({ name, ...pkg });
            }
        });

        resultsCount.textContent = filteredPackages.length;
        renderPackageCards();
    }

    function matchesActiveCategory(name, pkg) {
        if (currentCategory === 'all') return true;
        
        // Simple heuristic categories based on names/descriptions
        if (currentCategory === 'web') {
            return name.includes('http') || name.includes('web') || name.includes('net') || name.includes('api');
        }
        if (currentCategory === 'database') {
            return name.includes('db') || name.includes('sql') || name.includes('redis') || name.includes('mongo') || name.includes('json');
        }
        if (currentCategory === 'standard') {
            return name.includes('fs') || name.includes('math') || name.includes('json') || name.includes('regex') || name.includes('stl');
        }
        return true;
    }

    // Render cards to UI
    function renderPackageCards() {
        if (filteredPackages.length === 0) {
            packagesGrid.innerHTML = `
                <div class="loading-spinner-wrapper">
                    <p>No modules match the current search filters.</p>
                </div>
            `;
            return;
        }

        packagesGrid.innerHTML = '';
        filteredPackages.forEach(pkg => {
            const card = document.createElement('div');
            card.className = 'package-card';
            card.innerHTML = `
                <div class="card-header-row">
                    <h3 class="card-title">${pkg.name}</h3>
                    <span class="card-version">v${pkg.latest}</span>
                </div>
                <p class="card-description">${pkg.description}</p>
                <div class="card-meta">
                    <div class="card-meta-item">
                        <svg class="card-meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                        </svg>
                        <span>${pkg.license}</span>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-outline-card details-trigger" data-name="${pkg.name}">Details</button>
                    <button class="btn btn-secondary quick-install-trigger" data-name="${pkg.name}">Install</button>
                </div>
            `;
            
            // Add listeners to inside elements
            card.querySelector('.details-trigger').addEventListener('click', () => openDetailsModal(pkg.name));
            card.querySelector('.quick-install-trigger').addEventListener('click', (e) => {
                const btn = e.currentTarget;
                const cmd = `cl-pkg install ${pkg.name}`;
                navigator.clipboard.writeText(cmd);
                
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.style.color = '#34d399';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.color = '';
                }, 1500);
            });

            packagesGrid.appendChild(card);
        });
    }

    // Modal Control: Details
    function openDetailsModal(name) {
        const pkg = allPackages[name];
        if (!pkg) return;

        detailsName.textContent = name;
        detailsVersion.textContent = `v${pkg.latest}`;
        detailsDesc.textContent = pkg.description;
        detailsInstallCmd.textContent = `cl-pkg install ${name}`;
        
        // Grab git repo details
        const verInfo = (pkg.versions && pkg.versions[pkg.latest]) || {};
        detailsGitUrl.href = verInfo.url || `https://github.com/cl-andro/cluster-modules/tree/main/packages/${name}`;
        detailsLicense.textContent = pkg.license;
        detailsOutputPath.textContent = `cl_modules/${name}.cl`;

        detailsModal.classList.add('active');
    }

    // Modal triggers
    openPublishModalBtn.addEventListener('click', () => publishModal.classList.add('active'));
    closePublishModalBtn.addEventListener('click', () => publishModal.classList.remove('active'));
    closeDetailsModalBtn.addEventListener('click', () => detailsModal.classList.remove('active'));
    
    goToGithubBtn.addEventListener('click', () => {
        window.open('https://github.com/cl-andro/cluster-modules', '_blank');
        publishModal.classList.remove('active');
    });

    // Copy functions
    function handleCopy(text, btnElement) {
        navigator.clipboard.writeText(text);
        const icon = btnElement.innerHTML;
        btnElement.innerHTML = `
            <svg style="width: 1.15rem; height: 1.15rem; color: #34d399;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `;
        setTimeout(() => {
            btnElement.innerHTML = icon;
        }, 1500);
    }

    copyInstallBtn.addEventListener('click', () => {
        handleCopy(document.querySelector('.install-cmd').textContent, copyInstallBtn);
    });

    copyDetailsInstallBtn.addEventListener('click', () => {
        handleCopy(detailsInstallCmd.textContent, copyDetailsInstallBtn);
    });

    // Search input
    searchInput.addEventListener('input', applyFilters);

    // Sidebar filter buttons click event
    filterButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategory = e.currentTarget.dataset.category;
            applyFilters();
        });
    });

    // Close modals on clicking outside overlay
    window.addEventListener('click', (e) => {
        if (e.target === publishModal) publishModal.classList.remove('active');
        if (e.target === detailsModal) detailsModal.classList.remove('active');
    });
});
