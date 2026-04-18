        let sessionToken = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
        let debounceTimer;

        const searchInput = document.getElementById('address-search');
        const dropdown = document.getElementById('autocomplete-dropdown');
        
        searchInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (!val) {
                dropdown.classList.add('hidden');
                return;
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetch(`/api/eligibility/autocomplete?input=${encodeURIComponent(val)}&sessiontoken=${sessionToken}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.predictions && data.predictions.length > 0) {
                            dropdown.textContent = '';
                            data.predictions.forEach(p => {
                                const div = document.createElement('div');
                                div.className = 'px-4 py-3 hover:bg-white/10 cursor-pointer transition-colors text-sm font-medium';
                                div.onclick = () => selectPlace(p.place_id, p.description);
                                div.textContent = p.description;
                                dropdown.appendChild(div);
                            });
                            dropdown.classList.remove('hidden');
                        } else {
                            dropdown.classList.add('hidden');
                        }
                    })
                    .catch(err => console.error('Autocomplete error:', err));
            }, 300);
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });

        function selectPlace(placeId, description) {
            searchInput.value = description;
            dropdown.classList.add('hidden');
            // Refresh session token after successful selection
            sessionToken = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
            performSearch(placeId, description);
        }

        function setLoading(loading) {
            const btnText = document.getElementById('search-btn-text');
            const spinner = document.getElementById('search-spinner');
            const searchBtn = document.getElementById('search-btn');
            
            if (loading) {
                btnText.textContent = 'Searching...';
                spinner.classList.remove('hidden');
                searchBtn.disabled = true;
                searchBtn.classList.add('opacity-70', 'cursor-not-allowed');
            } else {
                btnText.textContent = 'Search';
                spinner.classList.add('hidden');
                searchBtn.disabled = false;
                searchBtn.classList.remove('opacity-70', 'cursor-not-allowed');
            }
        }

        function performSearch(placeId = null, description = null) {
            const address = description || document.getElementById('address-search').value;
            if (!address) return;

            setLoading(true);

            fetch('/api/eligibility/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address: address, place_id: placeId })
            })
            .then(r => r.json())
            .then(data => {
                const panel = document.getElementById('search-results');
                const badge = document.getElementById('search-status-badge');

                document.getElementById('search-address').innerText = data.address || address;
                document.getElementById('search-reason').innerText = data.plain_english_conditions || data.conditions || data.reason || 'No details available';

                const status = data.eligibility_status || data.status;
                badge.innerText = status || 'UNKNOWN';
                
                // Traffic Light UI logic
                const statusUpper = (status || '').toUpperCase();
                if (statusUpper === 'GREEN') {
                    badge.className = 'px-3 py-1 text-xs font-black uppercase rounded-[8px] bg-green-500/20 text-green-600';
                } else if (statusUpper === 'YELLOW') {
                    badge.className = 'px-3 py-1 text-xs font-black uppercase rounded-[8px] bg-yellow-500/20 text-yellow-600';
                } else if (statusUpper === 'RED') {
                    badge.className = 'px-3 py-1 text-xs font-black uppercase rounded-[8px] bg-red-500/20 text-red-600 animate-pulse';
                } else {
                    badge.className = 'px-3 py-1 text-xs font-black uppercase rounded-[8px] bg-gray-500/20 text-gray-600';
                }

                const permitLink = data.permit_application_url || data.permit_link;
                if (permitLink) {
                    document.getElementById('permit-link').href = permitLink;
                    document.getElementById('permit-link-container').classList.remove('hidden');
                } else {
                    document.getElementById('permit-link-container').classList.add('hidden');
                }

                panel.classList.remove('hidden');
            })
            .catch(err => {
                console.error('Search failed:', err);
                alert('Search failed. Please try again.');
            })
            .finally(() => setLoading(false));
        }

        function openAddPropertyModal() {
            document.getElementById('add-property-modal').classList.remove('hidden');
        }

        function closeAddPropertyModal() {
            document.getElementById('add-property-modal').classList.add('hidden');
            document.getElementById('add-property-form').reset();
        }

        function openFilterModal() {
            document.getElementById('filter-modal').classList.remove('hidden');
        }

        function closeFilterModal() {
            document.getElementById('filter-modal').classList.add('hidden');
        }

        function applyFilters() {
            const status = document.getElementById('filter-status').value;
            fetchProperties(status || null);
            closeFilterModal();
        }

        function clearFilters() {
            document.getElementById('filter-status').value = '';
            document.getElementById('filter-type').value = '';
        }

        document.getElementById('add-property-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const data = {
                address: formData.get('address'),
                city: formData.get('city'),
                state: formData.get('state'),
                zip_code: formData.get('zip_code'),
                property_type: formData.get('property_type'),
                hoa_status: formData.get('hoa_status') === 'on'
            };
            try {
                const response = await fetch('/api/properties/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (response.ok) {
                    closeAddPropertyModal();
                    fetchProperties();
                } else {
                    alert('Failed to add property. Please try again.');
                }
            } catch (err) {
                console.error('Error adding property:', err);
                alert('Failed to add property. Please try again.');
            }
        });

        document.getElementById('address-search').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });

        document.getElementById('search-btn').addEventListener('click', () => performSearch());

        let parcelMap;

        function initParcelMap(properties) {
            if (parcelMap) return;
            
            parcelMap = L.map('parcel-map').setView([39.0, -98.0], 4);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(parcelMap);
            
            properties.forEach(p => {
                if (p.lat && p.lng) {
                    const markerColor = p.zoning_status === 'Violation' ? '#ef4444' : 
                                       p.zoning_status === 'Pending' ? '#f59e0b' : '#0d9488';
                    
                    const marker = L.circleMarker([p.lat, p.lng], {
                        radius: 10,
                        fillColor: markerColor,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(parcelMap);
                    
                    marker.bindPopup(DOMPurify.sanitize(`
                        <div class="p-2">
                            <strong class="text-on-surface font-headline tracking-tight">${p.name}</strong><br>
                            <span class="text-gray-500 text-sm">${p.location}</span><br>
                            <span class="text-xs font-bold ${p.zoning_status === 'Violation' ? 'text-red-500' : p.zoning_status === 'Pending' ? 'text-yellow-500' : 'text-teal-500'}">${p.zoning_status}</span>
                        </div>
                    `));
                }
            });
        }

        async function generatePermit(event, propertyId) {
            event.stopPropagation();
            const button = event.target.closest('button');
            const originalText = button.textContent;
            
            try {
                button.disabled = true;
                button.textContent = '';
                const span = document.createElement('span');
                span.className = 'material-symbols-outlined text-sm animate-spin';
                span.textContent = 'progress_activity';
                button.appendChild(span);
                button.appendChild(document.createTextNode(' Generating...'));
                
                const response = await fetch('/api/permit-generator/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ property_id: propertyId })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to generate permit application');
                }
                
                const data = await response.json();
                
                // Show success modal or download PDF
                alert(`Permit Application Generated!\n\nApplication ID: ${data.application_id}\nCounty: ${data.county}\nStatus: ${data.compliance_status}\n\nRequired Documents:\n${data.required_documents.join('\n')}\n\nProcessing Time: ${data.estimated_processing_time}`);
                
            } catch (error) {
                console.error('Error generating permit:', error);
                alert('Failed to generate permit application. Please try again.');
            } finally {
                button.disabled = false;
                button.textContent = originalText;
            }
        }

        async function loadRecommendations(event, propertyId) {
            if (event) event.stopPropagation();
            
            const container = document.querySelector(`.recommendations-container[data-property-id="${propertyId}"]`);
            const contentDiv = container.querySelector('.recommendations-content');
            
            try {
                contentDiv.textContent = '';
                const pLoad = document.createElement('p');
                pLoad.className = 'text-xs text-gray-500 animate-pulse';
                pLoad.textContent = 'Loading recommendations...';
                contentDiv.appendChild(pLoad);
                
                const response = await fetch('/api/recommendation-engine/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ property_id: propertyId })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to load recommendations');
                }
                
                const data = await response.json();
                
                if (data.recommendations && data.recommendations.length > 0) {
                    const recommendationsHTML = data.recommendations
                        .slice(0, 3) // Show top 3 recommendations
                        .map(rec => {
                            const priorityColor = rec.priority === 'high' ? 'text-red-600' : 
                                                 rec.priority === 'medium' ? 'text-yellow-600' : 'text-gray-600';
                            return `<li class="${priorityColor}">${rec.title} ${rec.expected_impact ? `(${rec.expected_impact})` : ''}</li>`;
                        })
                        .join('');
                    
                    contentDiv.textContent = '';
                    
                    const scoreDiv = document.createElement('div');
                    scoreDiv.className = 'mb-2';
                    const scoreLabel = document.createElement('span');
                    scoreLabel.className = 'text-xs font-bold text-gray-500';
                    scoreLabel.textContent = 'Health Score: ';
                    const scoreVal = document.createElement('span');
                    scoreVal.className = 'text-xs font-bold text-primary';
                    scoreVal.textContent = data.overall_health_score.toFixed(1) + '%';
                    scoreDiv.appendChild(scoreLabel);
                    scoreDiv.appendChild(scoreVal);
                    contentDiv.appendChild(scoreDiv);
                    
                    const ul = document.createElement('ul');
                    ul.className = 'text-xs space-y-1 list-disc list-inside';
                    data.recommendations.slice(0, 3).forEach(rec => {
                        const li = document.createElement('li');
                        li.className = rec.priority === 'high' ? 'text-red-600' : rec.priority === 'medium' ? 'text-yellow-600' : 'text-gray-600';
                        li.textContent = rec.title + (rec.expected_impact ? ` (${rec.expected_impact})` : '');
                        ul.appendChild(li);
                    });
                    contentDiv.appendChild(ul);
                    
                    if (data.recommendations.length > 3) {
                        const pMore = document.createElement('p');
                        pMore.className = 'text-xs text-gray-500 mt-2';
                        pMore.textContent = `+${data.recommendations.length - 3} more recommendations`;
                        contentDiv.appendChild(pMore);
                    }
                } else {
                    contentDiv.textContent = '';
                    const pEmpty = document.createElement('p');
                    pEmpty.className = 'text-xs text-gray-600';
                    pEmpty.textContent = 'No recommendations available. Property is optimized!';
                    contentDiv.appendChild(pEmpty);
                }
                
            } catch (error) {
                console.error('Error loading recommendations:', error);
                contentDiv.textContent = '';
                const pErr = document.createElement('p');
                pErr.className = 'text-xs text-red-600';
                pErr.textContent = 'Failed to load recommendations';
                contentDiv.appendChild(pErr);
            }
        }

        function exportPDF(propertyId) {
            fetch(`/api/dashboard/compliance/history/${propertyId}`)
                .then(r => r.json())
                .then(data => {
                    const printWindow = window.open('', '_blank');
                    const html = `
                        <html>
                        <head><title>Compliance Report - ${data.property_name}</title>
                        <style>body{font-family:system-ui;padding:40px;}h1{color:#0d9488;}</style>    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.5/purify.min.js"><\/script>
</head>
                        <body>
                            <h1>Compliance Report: ${data.property_name}</h1>
                            <h2>History</h2>
                            <ul>${data.history.map(h => `<li>${h.date} - ${h.action} (${h.status})</li>`).join('')}</ul>
                            ${data.violations.length > 0 ? `<h2 style="color:red;">Violations</h2><ul>${data.violations.map(v => `<li>${v.date} - ${v.type}: ${v.description}</li>`).join('')}</ul>` : ''}
</body>
                        </html>
                    `;
                    printWindow.document.write(html);
                    printWindow.document.close();
                    printWindow.print();
                });
        }

        function renderSkeletons() {
            const grid = document.getElementById('property-grid');
            grid.textContent = '';
            const skelTemplate = document.getElementById('property-card-skeleton');
            for(let i=0; i<3; i++){
                grid.appendChild(skelTemplate.content.cloneNode(true));
            }
        }

        async function fetchProperties(filterStatus = null) {
            const grid = document.getElementById('property-grid');
            renderSkeletons();
            
            try {
                let url = '/api/v1/properties';
                if (filterStatus) {
                    url += `?status=${encodeURIComponent(filterStatus)}`;
                }
                const response = await fetch(url);
                if (!response.ok) {
                    if (response.status === 500 || response.status === 502 || response.status === 503 || response.status === 504) {
                        throw new Error('SYSTEM_DEGRADED');
                    }
                    throw new Error('Network response was not ok');
                }
                const properties = await response.json();
                renderProperties(properties);
                initParcelMap(properties);
            } catch (error) {
                console.error('Failed to fetch properties:', error);
                if (error.message === 'SYSTEM_DEGRADED' || error.message === 'Failed to fetch') {
                    grid.textContent = '';
                    const errTemplate = document.getElementById('system-degraded-error');
                    grid.appendChild(errTemplate.content.cloneNode(true));
                } else {
                    // Fallback mock data if other error
                    renderProperties([
                        { id: 1, name: "The Obsidian Sanctuary", location: "West Hollywood, CA", price: 1250, beds: 4, baths: 3.5, zoning_status: "Compliant", image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuDtDfxPMaRsQxdORVLEVnaJqJkfWn-BIXgFNQc-W5TalH7m8KmPsVxzaGJymts4o67euXEuPWg-baUXk4eMJfPEe5BNL4ewYRx5BGIISm6s-VSgn_4yYv07IC2nEmtgMELJXzcESUQg9C8Wd4ktY2bTxOBeFDG9fiGcZVp6tsDSSyt5Noy0pJAbcaZD7TEfNffu00ipN1I6qeoV-KfAp73nAnWN2l8WW7hV8bKR-DY9XH9gD1QXSQZzfO7x5soMp5tvDsIGbgRGAlw" },
                        { id: 2, name: "The Glass Pavilion", location: "Aspen, CO", price: 2400, beds: 5, baths: 6, zoning_status: "Pending", image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuBq14jjRyvZzz5UTQ0eMg5f3Tb372I7mv8Yrv6TY6sV_E4IRmFPA9xkERl57KcoDkzf8ltJE710_mWm9ijIJBp9YOOLmP9XuxQmdaJfrn4sqja-Py71hfXYXCpHUpb3lceiSPUTdzYkw_0n2v2n-UO4PvSh56L6oRhsLSfL2X0SP-VMGsDLeIH8Sw1pjKpBSnQQoYGfk5_wZ7qxULyQFOyddN3I7xAgbjPRLZFhFVQNfulIKKZDNVG_Jy01u1swzQDGBbk_ANZ95HE" },
                        { id: 3, name: "Azure Loft Estate", location: "Miami Beach, FL", price: 850, beds: 3, baths: 3, zoning_status: "Violation", image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuDNvPJa8r3BvpFcxDHWTuHvngW3w2L31pdYX1LsjjO8rspEk8_0xeqr01EkJ81bgS4QyRXhja146HIbo1pSks32I3W5U6kwhSPBWTMhhp4rhfXNbzGu-oVr3KCs97Co4_kJid2PFPsa_oEa2RpVcq2Hb5wVoxwOee45oOVauEJ_I02eRigIcTrVjre8HFqtFRmn16IwF-yTXMsL5HOXCf9-xWqKHPMMdKPXvQoBbFubq2ne4cxtT36bjDgrYexgaqKAAL8_nNHW0rM" }
                    ]);
                }
            }
        }

        
        function renderProperties(properties) {
            const grid = document.getElementById('property-grid');
            grid.textContent = '';
            const template = document.getElementById('property-card-template');

            properties.forEach(p => {
                const clone = template.content.cloneNode(true);
                
                const root = clone.querySelector('.property-card-root');
                const banner = clone.querySelector('.violation-banner');
                const imageContainer = clone.querySelector('.property-image-container');
                const image = clone.querySelector('.property-image');
                const statusBadge = clone.querySelector('.property-status-badge');
                const exportBtn = clone.querySelector('.property-export-btn');
                const name = clone.querySelector('.property-name');
                const location = clone.querySelector('.property-location');
                const price = clone.querySelector('.property-price');
                const beds = clone.querySelector('.property-beds');
                const baths = clone.querySelector('.property-baths');
                const county = clone.querySelector('.property-county');
                const permitBtn = clone.querySelector('.property-permit-btn');
                const recContainer = clone.querySelector('.recommendations-container');
                const refreshBtn = clone.querySelector('.property-refresh-btn');

                if (p.zoning_status === 'Violation') {
                    banner.classList.remove('hidden');
                    imageContainer.classList.add('mt-10');
                }

                image.src = p.image_url;
                image.alt = p.name;
                
                statusBadge.appendChild(createStatusBadge(p.zoning_status));
                
                exportBtn.addEventListener('click', () => exportPDF(p.id));
                name.textContent = p.name;
                location.textContent = p.location;
                price.textContent = '$' + p.price.toLocaleString();
                beds.textContent = p.beds;
                baths.textContent = p.baths;
                county.textContent = p.county || 'Pasco';
                
                permitBtn.addEventListener('click', (event) => generatePermit(event, p.id));
                
                recContainer.dataset.propertyId = p.id;
                refreshBtn.addEventListener('click', (event) => loadRecommendations(event, p.id));

                grid.appendChild(clone);
            });

            // Auto-load recommendations for each property
            properties.forEach(p => {
                setTimeout(() => loadRecommendations(null, p.id), 100);
            });
        }

        function createStatusBadge(status) {
            const span = document.createElement('span');
            span.className = "px-3 py-1 text-xs font-black uppercase rounded-[8px] flex items-center gap-1 ";
            
            const icon = document.createElement('span');
            icon.className = "material-symbols-outlined text-sm";
            icon.style.fontVariationSettings = "'FILL' 1";
            
            if (status === 'Compliant') {
                span.className += "bg-green-500/20 text-green-600";
                icon.textContent = 'verified_user';
                span.appendChild(icon);
                span.appendChild(document.createTextNode('Compliant'));
            } else if (status === 'Pending') {
                span.className += "bg-yellow-500/20 text-yellow-600";
                icon.textContent = 'pending';
                span.appendChild(icon);
                span.appendChild(document.createTextNode('Pending'));
            } else if (status === 'Violation') {
                span.className += "bg-red-500/20 text-red-600 animate-pulse";
                icon.textContent = 'warning';
                span.appendChild(icon);
                span.appendChild(document.createTextNode('Violation'));
            } else {
                span.className += "bg-white/10 text-white text-gray-500";
                span.textContent = 'Unknown';
            }
            return span;
        }

        document.addEventListener('DOMContentLoaded', () => {
            fetchProperties();
            
            // Fetch unified dashboard data for listing health metrics
            fetch('/api/dashboard/unified')
                .then(r => r.json())
                .then(data => {
                    // Update compliance score
                    document.querySelector('.compliance-score').innerText = `${data.overall_compliance_score}%`;
                    
                    // Update active alerts
                    const alertsFormatted = String(data.total_active_alerts).padStart(2, '0');
                    document.querySelector('.active-alerts').innerText = alertsFormatted;
                    
                    // Update total properties count if needed
                    // You could add more dashboard stats here
                })
                .catch(err => {
                    console.error('Failed to fetch dashboard stats:', err);
                    // Fallback to default values
                    document.querySelector('.compliance-score').innerText = '99.1%';
                    document.querySelector('.active-alerts').innerText = '01';
                });
        });

        async function upgradeToPro() {
            try {
                const response = await fetch('/api/subscriptions/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tier: 'pro' })
                });
                if (!response.ok) throw new Error('Checkout failed');
                const data = await response.json();
                if (data.checkout_url) {
                    window.location.href = data.checkout_url;
                } else if (data.message) {
                    alert('Subscription initiated: ' + data.message);
                } else {
                    alert('Redirecting to checkout...');
                }
            } catch (error) {
                console.error('Error initiating subscription:', error);
                alert('Failed to start checkout process.');
            }
        }

        async function generateCompliancePDF() {
            try {
                const response = await fetch('/api/documents/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        property_address: '123 Hosteva Way, Cloud City, FL 33000',
                        county: 'Cloud County'
                    })
                });
                if (!response.ok) throw new Error('PDF generation failed');
                const data = await response.json();
                alert('PDF Generation Status: ' + (data.status || 'Pending') + '\\nTask ID: ' + (data.task_id || 'N/A') + '\\nMessage: ' + (data.message || ''));
            } catch (error) {
                console.error('Error generating PDF:', error);
                alert('Failed to initiate PDF generation.');
            }
        }
