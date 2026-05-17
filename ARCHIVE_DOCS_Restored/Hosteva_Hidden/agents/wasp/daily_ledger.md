- Removed duplicated Tailwind CDN scripts and config from landing.html and dashboard.html
- Removed redundant .material-symbols-outlined style blocks from landing.html and dashboard.html
- Calculated md5sum hashes and submitted API handshake for BUG-003
- Completed TICKET-05: Integrated /api/v1/dashboard/overview into dashboard.html and updated DOM elements (quota_remaining, subscription_tier, recent_queries).
[BUG-005] Re-injected tailwindcss script, fixed missing <style> tag opening in landing.html, and stripped broken image fallback on logo. MD5: 3cb0e9cfafd56cb11e1ad122bd9e3a18. Pushed state to AUDITING.
