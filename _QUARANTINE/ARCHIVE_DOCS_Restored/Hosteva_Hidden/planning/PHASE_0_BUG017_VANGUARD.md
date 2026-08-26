# Phase 0: Vanguard Planning (Eradicate Dynamic Design Tokens)
**Date:** 2026-04-16
**Goal:** Sever the asynchronous Google Stitch API dependency and hard-code design tokens natively via Tailwind CSS.
**Targets:** BUG-017

## Vanguard Consensus & Architectural Alignment

**Wasp (Lead UI/UX):** 
"The Secretary is right. Pinging an external API just to paint the `PropertyCardSkeleton` or standard UI components is an unnecessary bottleneck. I will strip out the dynamic fetch logic inside the root `layout.tsx` (or `base.html` template). I will extract the exact hex codes, border radii, and spacing variables we pulled during SPIKE-005 and permanently inject them into `tailwind.config.js` under the `theme.extend` object."

**Iron Man (CTO - Architecture):** 
"I'll scrub the `app/api/routes/` and `.env` files. I will physically remove the `STITCH_API_KEY` and any backend route that proxies CSS/theme token fetches. The backend should only serve raw JSON compliance data, not design tokens."

**Ant-Man (Optimization):** 
"Hard-coding the Tailwind config means we can finally utilize PurgeCSS locally. The build step will analyze our HTML/React files and strip out thousands of unused CSS classes before deployment. Our final CSS bundle size will drop from ~400KB down to ~15KB, instantly accelerating page load speeds."

**Hawkeye (Product Owner):** 
"The strategy is sound and aligns perfectly with the Secretary's mandate to eliminate external rate-limiting risks for the MVP. BUG-017 is locked onto the board."