Google Stitch Source: https://stitch.withgoogle.com/projects/6411392088286229161?pli=1

# Hosteva Design Baseline

## 1. Core Principles
- **The "No-Line" Rule**: Default borders are strictly prohibited (`border-none`). Layout separation is achieved through shadows, spacing, and glassmorphism instead of hard lines.

## 2. Global Design Tokens
- **Glassmorphism Base**: `backdrop-blur-[20px]`
- **Border Radius**: `rounded-[8px]`
- **Borders**: `border-none`

## 3. Component Styling
### Autocomplete Dropdown & General Containers
- Background & Blur: `bg-white/10 backdrop-blur-md`
- Shadow: `shadow-2xl` (or `shadow-ambient`)
- Borders: `border-none`

### Traffic Light UI (Compliance Status)
Used for the `eligibility_status` badges to communicate regulatory conditions clearly. All badges share the base styling of `px-3 py-1 text-xs font-black uppercase rounded-[8px] shadow-ambient backdrop-blur-[20px] border-none`.

- **GREEN (Compliant)**: 
  - Classes applied: `bg-green-500/20 text-green-600`
- **YELLOW (Manual Review / Pending)**:
  - Classes applied: `bg-yellow-500/20 text-yellow-600`
- **RED (Violation / Not Eligible)**:
  - Classes applied: `bg-red-500/20 text-red-600 animate-pulse`
