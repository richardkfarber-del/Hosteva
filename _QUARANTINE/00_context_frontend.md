# Core Project Context
# Project Overview: Hosteva

## What is it?
Hosteva is the "Iron Man Suit" for short-term rental hosts. It is a mobile and web application designed to help hosts navigate the increasingly complex world of STR compliance, taxes, and listing requirements.

## Problem We Are Solving
In Florida (specifically Pasco and Hillsborough counties), the laws change weekly. Hosts are getting fined or delisted because they can't keep up.

## The Solution
A smart assistant that:
1. Scrapes local ordinances to find compliance gaps.
2. Automatically generates the necessary paperwork for permits.
3. Optimizes listing descriptions to ensure they are "Search-Safe" and "Platform-Compliant."



## UI/UX Design State
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

## 7. Logo Dimensionality Assessment (Wasp)
The current `h-8 w-auto` utility classes are optimized for traditional, horizontally-oriented wordmarks. Because the new Hosteva logo utilizes a square (1:1) aspect ratio for its shield/prism design, restricting the height to `h-8` (32px) proportionately restricts the width to 32px. This creates a microscopic, illegible footprint within the sidebar container.
**Mandate:**
- **Remove:** `h-8 w-auto`
- **Apply Logo Sizing:** Use `h-16 w-16` or `h-20 w-20` (64px to 80px) to provide the square mark with appropriate visual weight and screen real estate.
- **Apply Object Constraints:** Add `object-contain` to guarantee the shield never distorts across viewport changes.
- **Parent Container Alignment:** Upgrade the current parent wrapper (`mb-8 px-2`) to utilize flexbox for proper centering of the heavier square asset. Apply `flex justify-center items-center mb-8 px-2`.

