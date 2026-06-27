// wizard.js - Property Onboarding Wizard Validation Logic

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-property-form');
    if (!form) return;

    // Clone the form to clear any pre-existing inline submit listeners
    const clonedForm = form.cloneNode(true);
    form.parentNode.replaceChild(clonedForm, form);

    // Register our new, validated onboarding wizard submit handler
    clonedForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = clonedForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Add Property';
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="material-symbols-outlined animate-spin text-sm">progress_activity</span> Validating...';
        }

        const formData = new FormData(clonedForm);
        const address = formData.get('address');
        const city = formData.get('city');
        const state = formData.get('state');
        const zipCode = formData.get('zip_code') || '';
        const zoningCode = formData.get('zoning_code') || '';
        const propertyType = formData.get('property_type') || '';
        const intendedStay = formData.get('intended_stay_duration') || 'nightly';

        try {
            // Step 1: Pre-validation gating check
            const validateResp = await fetch('/api/v1/onboarding/validate-property', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    property_id: 0, // Dummy ID for pre-validation
                    city: city,
                    zip_code: zipCode,
                    zoning_code: zoningCode,
                    property_type: propertyType,
                    intended_stay_duration: intendedStay
                })
            });

            if (!validateResp.ok) {
                throw new Error('Validation service returned error status ' + validateResp.status);
            }

            const validation = await validateResp.json();

            // Step 2: If validation fails, halt wizard with a polished modal
            if (!validation.allowed) {
                showHaltingModal(validation.reason || validation.rejection_reason || "Short-term rentals are restricted in this municipality.");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
                return;
            }

            // Step 3: If validation passes, create property in database via POST /api/v1/properties
            const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || localStorage.getItem("token") || sessionStorage.getItem("token") || getCookie("access_token");
            const headers = { 'Content-Type': 'application/json' };
            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const createResp = await fetch('/api/v1/properties/', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    address: {
                        address: address,
                        city: city,
                        state: state,
                        zip_code: zipCode
                    },
                    property_type: propertyType,
                    compliance_data: {
                        zoning_status: validation.status === "REJECTED" ? "Violation" : validation.status === "PASSED" ? "Compliant" : "Pending",
                        hoa_status: validation.reason && (validation.reason.toLowerCase().includes("hoa") || validation.reason.toLowerCase().includes("covenants")) ? true : false,
                        required_permits: validation.requires_permit ? [validation.permit_name || "STR Permit"] : [],
                        local_restrictions: validation.warning ? { "Warning": validation.warning } : {}
                    }
                })
            });

            if (!createResp.ok) {
                throw new Error('Failed to create property profile.');
            }

            const newProperty = await createResp.json();
            const actualPropertyId = newProperty.id;

            // Step 4: Call validate endpoint with actual property ID to generate checklist tasks
            await fetch('/api/v1/onboarding/validate-property', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    property_id: actualPropertyId,
                    city: city,
                    zip_code: zipCode,
                    zoning_code: zoningCode,
                    property_type: propertyType,
                    intended_stay_duration: intendedStay
                })
            });

            // Step 5: Close modal, refresh dashboard and show notifications
            if (typeof window.closeAddPropertyModal === 'function') {
                window.closeAddPropertyModal();
            } else {
                clonedForm.reset();
                document.getElementById('add-property-modal').classList.add('hidden');
            }

            if (typeof window.fetchProperties === 'function') {
                window.fetchProperties();
            }

            // Step 6: Polished Notifications/Toasts for warnings and permits
            if (validation.requires_permit) {
                showPermitNotification(validation.permit_name || "Conditional Use Permit (CUP)");
            }
            if (validation.warning) {
                showWarningNotification(validation.warning);
            }

        } catch (err) {
            console.error('Onboarding Wizard Error:', err);
            alert('An error occurred during onboarding: ' + err.message);
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        }
    });
});

// Highly polished error modal halting the onboarding wizard
function showHaltingModal(reason) {
    // Remove existing halting modal if any
    const existing = document.getElementById('halting-modal');
    if (existing) existing.remove();

    const modalHtml = `
    <div id="halting-modal" class="fixed inset-0 bg-[#001c37]/75 backdrop-blur-sm z-[100] flex items-center justify-center animate-fade-in" style="transition: all 0.3s ease;">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden border border-red-100 flex flex-col p-8 items-center text-center relative" style="transform: scale(1); transition: transform 0.3s ease;">
            <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mb-6 text-red-500 border border-red-100 animate-pulse">
                <span class="material-symbols-outlined text-3xl font-bold">block</span>
            </div>
            <h3 class="font-headline text-2xl font-black text-slate-800 mb-3 uppercase italic tracking-tight">Onboarding Blocked</h3>
            <p class="text-slate-600 text-sm leading-relaxed mb-6 font-medium">${reason}</p>
            <button onclick="document.getElementById('halting-modal').remove()" class="w-full py-3.5 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-colors shadow-lg uppercase tracking-wider text-xs font-headline">
                Close & Acknowledge
            </button>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Highly polished slide-in notification for permit requirements
function showPermitNotification(permitName) {
    const existing = document.getElementById('permit-notification');
    if (existing) existing.remove();

    const notificationHtml = `
    <div id="permit-notification" class="fixed bottom-6 right-6 z-[100] bg-slate-900 text-white p-6 rounded-2xl shadow-2xl flex items-center gap-4 border border-teal-500/20 max-w-md" style="animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;">
        <span class="material-symbols-outlined text-teal-400 text-3xl shrink-0">info</span>
        <div>
            <h4 class="font-headline font-bold text-sm text-teal-400 mb-1">Permit Guidance Active</h4>
            <p class="text-xs text-slate-300 leading-relaxed">This property requires a <strong>${permitName}</strong>. Hosteva will guide you through securing your permit step-by-step.</p>
        </div>
        <button onclick="document.getElementById('permit-notification').remove()" class="text-slate-400 hover:text-white transition-colors shrink-0">
            <span class="material-symbols-outlined text-sm">close</span>
        </button>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', notificationHtml);
    injectAnimationStyles();
    
    setTimeout(() => {
        const notif = document.getElementById('permit-notification');
        if (notif) notif.remove();
    }, 10000);
}

// Highly polished slide-in notification for warnings
function showWarningNotification(warning) {
    const existing = document.getElementById('warning-notification');
    if (existing) existing.remove();

    const notificationHtml = `
    <div id="warning-notification" class="fixed bottom-6 right-6 z-[100] bg-slate-900 text-white p-6 rounded-2xl shadow-2xl flex items-center gap-4 border border-yellow-500/20 max-w-md" style="animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;">
        <span class="material-symbols-outlined text-yellow-400 text-3xl shrink-0">warning</span>
        <div>
            <h4 class="font-headline font-bold text-sm text-yellow-400 mb-1">Stay Duration Warning</h4>
            <p class="text-xs text-slate-300 leading-relaxed">${warning}</p>
        </div>
        <button onclick="document.getElementById('warning-notification').remove()" class="text-slate-400 hover:text-white transition-colors shrink-0">
            <span class="material-symbols-outlined text-sm">close</span>
        </button>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', notificationHtml);
    injectAnimationStyles();

    setTimeout(() => {
        const notif = document.getElementById('warning-notification');
        if (notif) notif.remove();
    }, 10000);
}

// Helper to inject animations if not already present
function injectAnimationStyles() {
    if (document.getElementById('wizard-toast-styles')) return;
    const styles = `
    @keyframes slideIn {
        from { transform: translateX(120%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }`;
    const styleEl = document.createElement('style');
    styleEl.id = 'wizard-toast-styles';
    styleEl.innerHTML = styles;
    document.head.appendChild(styleEl);
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
