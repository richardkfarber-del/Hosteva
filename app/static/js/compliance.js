// app/static/js/compliance.js

(function() {
    console.log("Compliance JS Loaded");

    if (typeof DOMPurify !== 'undefined' && DOMPurify.setConfig) {
        DOMPurify.setConfig({ ADD_ATTR: ['onclick'] });
    }

    // Hidden input files element creation helper
    function getOrCreateFileInput() {
        let fileInput = document.getElementById('compliance-file-upload-input');
        if (!fileInput) {
            fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.id = 'compliance-file-upload-input';
            fileInput.className = 'hidden';
            fileInput.accept = '.pdf,.png,.jpg,.jpeg';
            fileInput.onchange = handleComplianceFileUpload;
            document.body.appendChild(fileInput);
        }
        return fileInput;
    }

    window.uploadComplianceDocument = function(checklistItemId) {
        window.uploadTargetChecklistItemId = checklistItemId;
        const fileInput = getOrCreateFileInput();
        fileInput.click();
    };

    async function handleComplianceFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const checklistItemId = window.uploadTargetChecklistItemId;
        if (!checklistItemId) return;

        // Reset file input value so selection triggers change again next time
        event.target.value = '';

        // Create notification banner
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-24 right-8 z-50 bg-[#001c37] text-white p-6 rounded-xl shadow-2xl flex items-center gap-4 border border-[#75fbbf]/20 transition-all duration-300';
        notification.innerHTML = `
            <span class="material-symbols-outlined text-[#75fbbf] animate-spin text-2xl">progress_activity</span>
            <div>
                <h4 class="font-headline font-bold text-sm">Auditing Document...</h4>
                <p class="text-xs text-gray-400">AI Compliance Engine is verifying credentials.</p>
            </div>
        `;
        document.body.appendChild(notification);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('checklist_item_id', checklistItemId);

        try {
            const resp = await fetch('/api/v1/compliance/audit-document', {
                method: 'POST',
                headers: {
                    'Authorization': headers['Authorization'] || ''
                },
                body: formData
            });

            const data = await resp.json();

            if (resp.ok && data.status === 'APPROVED') {
                notification.innerHTML = `
                    <span class="material-symbols-outlined text-[#75fbbf] text-2xl">check_circle</span>
                    <div>
                        <h4 class="font-headline font-bold text-sm text-[#75fbbf]">Audit Approved!</h4>
                        <p class="text-xs text-gray-400">Document matches property records perfectly.</p>
                    </div>
                `;
            } else {
                const reason = data.rejection_notes || 'Validation failed.';
                notification.innerHTML = `
                    <span class="material-symbols-outlined text-red-500 text-2xl">cancel</span>
                    <div>
                        <h4 class="font-headline font-bold text-sm text-red-500">Audit Rejected!</h4>
                        <p class="text-xs text-gray-400 truncate max-w-xs" title="${reason}">${reason}</p>
                    </div>
                `;
            }

            // Refresh properties list
            if (typeof fetchProperties === 'function') {
                // Wait briefly before reloading to let the database transaction settle
                setTimeout(async () => {
                    await fetchProperties();
                    if (window.currentTaskCategory) {
                        renderTasksList();
                    }
                }, 500);
            }

            setTimeout(() => {
                notification.remove();
            }, 6000);

        } catch (err) {
            console.error('Error auditing document:', err);
            notification.innerHTML = `
                <span class="material-symbols-outlined text-red-500 text-2xl">error</span>
                <div>
                    <h4 class="font-headline font-bold text-sm text-red-500">System Error</h4>
                    <p class="text-xs text-gray-400">Failed to connect to AI Auditor.</p>
                </div>
            `;
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }
    }

    // Override handleTaskAction to support checklistItem upload flow
    window.handleTaskAction = function(actionType, propertyId, index, checklistItemId) {
        if (actionType === 'complete_permit' && checklistItemId) {
            window.location.href = '/dashboard/tasks/' + checklistItemId;
        } else {
            // Original action fallbacks
            if (actionType === 'upload_hoa') {
                window.uploadTargetPropertyId = propertyId;
                const fileInput = document.getElementById('hoa-file-upload-input');
                if (fileInput) {
                    fileInput.click();
                }
            } else if (actionType === 'complete_permit') {
                alert('Initiating automated permit generation and registration workflow...');
            } else if (actionType === 'acknowledge_rule') {
                alert('Restriction Ordinance acknowledged. Compliance checklist updated!');
            } else if (actionType === 'flagged_violation') {
                alert('Warning: This property is flagged with a High Risk lease restriction. Short term renting is highly constrained by the HOA/jurisdiction.');
            }
        }
    };

    // Override renderTasksList
    window.renderTasksList = async function() {
        const container = document.getElementById('tasks-sections-container');
        const emptyState = document.getElementById('tasks-empty-state');
        const urgentGrid = document.getElementById('urgent-tasks-grid');
        const upcomingList = document.getElementById('upcoming-tasks-list');
        
        if (!container || !urgentGrid || !upcomingList) return;

        const properties = window.allProperties || [];
        let allTasks = [];

        // Fetch checklist items for all properties in parallel
        const checklistPromises = properties.map(p => 
            fetch(`/api/v1/compliance/checklist-items/${p.id}`, { headers })
                .then(res => res.ok ? res.json() : [])
                .catch(() => [])
        );

        let propertyChecklists = [];
        try {
            propertyChecklists = await Promise.all(checklistPromises);
        } catch (e) {
            console.error("Error fetching checklist items:", e);
        }

        properties.forEach((p, pIdx) => {
            const restrictions = p.local_restrictions || {};
            const checklistItems = propertyChecklists[pIdx] || [];

            // 1. HOA rule missing
            const isActionRequired = p.zoning_status && p.zoning_status.toLowerCase() === 'action required';
            if (isActionRequired) {
                allTasks.push({
                    type: 'hoa',
                    urgent: true,
                    title: 'HOA Detected: Public rules unavailable. Please upload governing documents for AI scanning.',
                    propertyAddress: p.address,
                    propertyId: p.id,
                    priority: 'Action Required',
                    badgeClass: 'bg-error-container text-on-error-container text-[10px] font-bold uppercase tracking-wider rounded-full',
                    actionText: 'Upload HOA Docs',
                    actionType: 'upload_hoa'
                });
            }

            // 2. Add checklist items from DB
            checklistItems.forEach(item => {
                const isApproved = item.status === 'APPROVED';
                const isRejected = item.status === 'REJECTED';
                
                let badgeClass = '';
                let priority = 'Required Permit';
                let actionText = 'Complete Now';
                let actionType = 'complete_permit';
                
                if (isApproved) {
                    priority = 'Approved';
                    badgeClass = 'bg-green-100 text-green-800 text-[10px] font-bold uppercase tracking-wider rounded-full flex items-center gap-1';
                    actionText = 'Verified';
                    actionType = 'verified_permit';
                } else if (isRejected) {
                    priority = 'Rejected';
                    badgeClass = 'bg-red-100 text-red-800 text-[10px] font-bold uppercase tracking-wider rounded-full flex items-center gap-1 relative group cursor-help border border-red-200';
                    actionText = 'Re-upload';
                    actionType = 'complete_permit';
                } else {
                    priority = 'Required Permit';
                    badgeClass = 'bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider rounded-full';
                    actionText = 'Complete Now';
                    actionType = 'complete_permit';
                }

                allTasks.push({
                    type: 'compliance',
                    urgent: !isApproved,
                    title: item.violation_notes,
                    propertyAddress: p.address,
                    propertyId: p.id,
                    checklistItemId: item.id,
                    priority: priority,
                    badgeClass: badgeClass,
                    actionText: actionText,
                    actionType: actionType,
                    status: item.status,
                    rejectionNotes: item.rejection_notes
                });
            });

            // 3. Add local restrictions
            for (const [key, val] of Object.entries(restrictions)) {
                const isHighRisk = val.toLowerCase().includes('minimum') || 
                                   val.toLowerCase().includes('month') || 
                                   val.toLowerCase().includes('lease') ||
                                   val.toLowerCase().includes('prohibit');
                allTasks.push({
                    type: 'compliance',
                    urgent: false,
                    title: `Review ${key} Ordinance`,
                    description: val,
                    propertyAddress: p.address,
                    propertyId: p.id,
                    priority: isHighRisk ? 'High Risk' : 'Local Rule',
                    badgeClass: isHighRisk ? 'bg-error-container text-on-error-container text-[10px] font-bold uppercase tracking-wider rounded-full' : 'bg-slate-100 text-slate-700 text-[10px] font-bold uppercase tracking-wider rounded-full',
                    actionText: isHighRisk ? 'Flagged Violation' : 'Acknowledge',
                    actionType: isHighRisk ? 'flagged_violation' : 'acknowledge_rule',
                    isHighRisk: isHighRisk
                });
            }
        });

        // Apply Category Filter
        let filteredTasks = allTasks;
        if (window.currentTaskCategory !== 'all') {
            filteredTasks = filteredTasks.filter(t => t.type === window.currentTaskCategory);
        }

        // Apply Search Query Filter
        if (window.currentTaskSearchQuery) {
            const q = window.currentTaskSearchQuery;
            filteredTasks = filteredTasks.filter(t => 
                t.title.toLowerCase().includes(q) || 
                t.propertyAddress.toLowerCase().includes(q) || 
                (t.description && t.description.toLowerCase().includes(q))
            );
        }

        if (filteredTasks.length === 0) {
            container.classList.add('hidden');
            emptyState.classList.remove('hidden');
            emptyState.classList.add('flex');
            return;
        }

        container.classList.remove('hidden');
        emptyState.classList.add('hidden');
        emptyState.classList.remove('flex');

        const urgentTasks = filteredTasks.filter(t => t.urgent);
        const upcomingTasks = filteredTasks.filter(t => !t.urgent);

        // Populate Urgent Tasks
        const urgentSection = document.getElementById('urgent-tasks-section');
        if (urgentTasks.length === 0) {
            if (urgentSection) urgentSection.classList.add('hidden');
        } else {
            if (urgentSection) urgentSection.classList.remove('hidden');
            let urgentGridHTML = '';
            urgentTasks.forEach((t, idx) => {
                const isHOA = t.actionType === 'upload_hoa';
                
                let badgeHTML = `<span class="${t.badgeClass}">${t.priority}</span>`;
                if (t.status === 'REJECTED') {
                    badgeHTML = `
                        <span class="${t.badgeClass}" style="position: relative;">
                            <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">cancel</span>
                            Rejected
                            <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 hidden group-hover:block bg-[#001c37] text-white text-xs p-2 rounded shadow-xl border border-red-500/20 normal-case font-normal z-50">
                                ${t.rejectionNotes}
                            </span>
                        </span>
                    `;
                } else if (t.status === 'APPROVED') {
                    badgeHTML = `
                        <span class="${t.badgeClass}">
                            <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">check_circle</span>
                            Approved
                        </span>
                    `;
                }

                let buttonHTML = `<button onclick="handleTaskAction('${t.actionType}', '${t.propertyId}', ${idx}, '${t.checklistItemId || ''}')" class="bg-primary hover:opacity-90 text-on-primary px-5 py-2 rounded font-semibold text-sm transition-opacity">${t.actionText}</button>`;
                if (t.status === 'APPROVED') {
                    buttonHTML = `<button disabled class="bg-slate-200 text-slate-500 px-5 py-2 rounded font-semibold text-sm cursor-not-allowed">Verified</button>`;
                }

                urgentGridHTML += `
                    <div class="bg-surface-container-lowest p-6 rounded-xl task-card-shadow border border-outline-variant/15 group hover:translate-y-[-4px] transition-all duration-300">
                        <div class="flex justify-between items-start mb-4">
                            ${badgeHTML}
                            <span class="material-symbols-outlined text-outline group-hover:text-primary transition-colors cursor-pointer">more_vert</span>
                        </div>
                        <h3 class="text-lg font-headline font-bold text-on-surface mb-1">${t.title}</h3>
                        <p class="text-on-surface-variant text-sm mb-4 flex items-center gap-1">
                            <span class="material-symbols-outlined text-sm text-primary">location_on</span> ${t.propertyAddress}
                        </p>
                        <div class="flex items-center justify-between mt-6">
                            <div class="flex flex-col">
                                <span class="text-[10px] uppercase text-outline font-bold">Priority</span>
                                <span class="text-sm font-semibold ${isHOA ? 'text-red-600' : t.status === 'REJECTED' ? 'text-red-600' : 'text-primary'}">${isHOA ? 'Critical' : t.status === 'REJECTED' ? 'Rejected' : 'High Priority'}</span>
                            </div>
                            ${buttonHTML}
                        </div>
                    </div>
                `;
            });
            urgentGrid.innerHTML = DOMPurify.sanitize(urgentGridHTML);
        }

        // Populate Upcoming Tasks
        const upcomingSection = document.getElementById('upcoming-tasks-section');
        if (upcomingTasks.length === 0) {
            if (upcomingSection) upcomingSection.classList.add('hidden');
        } else {
            if (upcomingSection) upcomingSection.classList.remove('hidden');
            let upcomingListHTML = '';
            upcomingTasks.forEach((t, idx) => {
                const statusText = t.status === 'APPROVED' ? 'Approved' : t.isHighRisk ? 'High Risk' : 'Awaiting Review';
                const statusColor = t.status === 'APPROVED' ? 'text-green-600 font-bold' : t.isHighRisk ? 'text-error font-bold animate-pulse' : 'text-secondary';
                const btnClass = t.isHighRisk ? 'bg-error text-white px-4 py-2 rounded text-sm font-bold hover:bg-error/90 shrink-0' : 'bg-surface-container-highest text-primary px-4 py-2 rounded text-sm font-bold';
                
                let buttonHTML = `<button onclick="handleTaskAction('${t.actionType}', '${t.propertyId}', ${idx}, '${t.checklistItemId || ''}')" class="${btnClass}">${t.actionText}</button>`;
                if (t.status === 'APPROVED') {
                    buttonHTML = `<button disabled class="bg-slate-100 text-slate-400 px-4 py-2 rounded text-sm font-bold cursor-not-allowed">Verified</button>`;
                }

                let upcomingStatusHTML = `<span class="text-sm font-medium ${statusColor}">${statusText}</span>`;
                if (t.status === 'REJECTED') {
                    upcomingStatusHTML = `
                        <span class="text-sm font-bold text-red-600 cursor-help relative group" style="position: relative;">
                            Rejected
                            <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 hidden group-hover:block bg-[#001c37] text-white text-xs p-2 rounded shadow-xl border border-red-500/20 normal-case font-normal z-50">
                                ${t.rejectionNotes}
                            </span>
                        </span>
                    `;
                } else if (t.status === 'APPROVED') {
                    upcomingStatusHTML = `<span class="text-sm font-bold text-green-600">Approved</span>`;
                }

                upcomingListHTML += `
                    <div class="bg-surface-container-low p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 border ${t.isHighRisk ? 'border-error/30' : 'border-transparent'} hover:border-outline-variant/20 transition-all">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 ${t.isHighRisk ? 'bg-error-container text-on-error-container' : 'bg-surface-container-lowest text-primary'} rounded-lg flex items-center justify-center shrink-0">
                                <span class="material-symbols-outlined">${t.isHighRisk ? 'warning' : 'rule'}</span>
                            </div>
                            <div>
                                <h3 class="font-bold text-on-surface flex items-center gap-2">
                                    ${t.title}
                                    ${t.isHighRisk ? `<span class="px-2 py-0.5 text-[9px] bg-error-container text-on-error-container font-black uppercase rounded">Violation Risk</span>` : ''}
                                </h3>
                                <p class="text-xs text-on-surface-variant">${t.propertyAddress} • <span class="${t.isHighRisk ? 'text-error font-semibold' : ''}">${t.description || 'Internal restriction guideline'}</span></p>
                            </div>
                        </div>
                        <div class="flex items-center gap-6 shrink-0">
                            <div class="text-right hidden md:block">
                                <span class="text-[10px] uppercase text-outline font-bold block">Status</span>
                                ${upcomingStatusHTML}
                            </div>
                            ${buttonHTML}
                        </div>
                    </div>
                `;
            });
            upcomingList.innerHTML = DOMPurify.sanitize(upcomingListHTML);
        }
    };
})();
