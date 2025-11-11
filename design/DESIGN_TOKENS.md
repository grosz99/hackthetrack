# Design Tokens Reference
**Racing Driver Analytics Dashboard**

This document defines all design tokens (colors, typography, spacing, etc.) that should be used throughout the application.

---

## Color Palette

### Primary Colors

```css
/* Brand Red */
--color-primary:        #EB0A1E  /* Main brand color - use for CTAs, accents */
--color-primary-dark:   #c20818  /* Hover states, darker accents */
--color-primary-light:  #ff1a2e  /* Lighter accents, backgrounds */
```

**Usage:**
- Primary buttons
- Navigation active states
- Important metrics/badges
- Border accents on key cards

**DO:**
```css
background: var(--color-primary);
border: 4px solid var(--color-primary);
```

**DON'T:**
```css
background: #e74c3c;  /* Wrong red! */
border: 4px solid #EB0A1E;  /* Use variable, not hardcoded */
```

---

### Background Colors

```css
/* Light Theme Backgrounds */
--color-bg-white:       #ffffff  /* Primary background for cards */
--color-bg-light:       #f9fafb  /* Secondary background */
--color-bg-gray:        #f3f4f6  /* Tertiary background, inactive states */

/* Dark Theme Backgrounds */
--color-bg-dark:        #0a0a0a  /* Page background (dark theme) */
--color-bg-darker:      #1a1a1a  /* Card backgrounds on dark pages */
--color-bg-darkest:     #000000  /* Pure black - use sparingly */
```

**Dark Page Pattern:**
```
┌─────────────────────────────────────┐
│ Page Container: #0a0a0a (dark)      │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Card: #ffffff (white)         │ │
│  │                               │ │
│  │  ┌─────────────────────────┐  │ │
│  │  │ Nested: #f9fafb (light) │  │ │
│  │  └─────────────────────────┘  │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

### Text Colors

```css
/* Light Theme Text */
--color-text-primary:   #1d1d1f  /* Body text on light backgrounds */
--color-text-secondary: #86868b  /* Secondary text, less emphasis */
--color-text-muted:     #6e6e73  /* Tertiary text, labels */

/* Dark Theme Text */
--color-text-inverse:   #ffffff  /* Text on dark backgrounds */
--color-text-gray-dark: #888888  /* Secondary text on dark backgrounds */
```

**Text Hierarchy Example:**
```html
<div style="background: #ffffff;">
  <h1 style="color: var(--color-text-primary);">Main Heading</h1>
  <p style="color: var(--color-text-secondary);">Subheading or description</p>
  <span style="color: var(--color-text-muted);">Label or metadata</span>
</div>
```

---

### Semantic Colors (Stats/Status)

```css
/* Percentile-Based Colors */
--color-stat-elite:     #f57f17  /* 90-100th percentile (gold) */
--color-stat-great:     #2e7d32  /* 75-89th percentile (green) */
--color-stat-good:      #1565c0  /* 60-74th percentile (blue) */
--color-stat-average:   #c2185b  /* 40-59th percentile (magenta) */
--color-stat-poor:      #d32f2f  /* 0-39th percentile (red) */
```

**Usage Rules:**
- Use for performance metrics only (consistency, racecraft, speed, tire mgmt)
- DO NOT use for generic UI elements
- Always pair with percentage text for context

**Example:**
```html
<div class="stat-badge" style="background: #f57f17;">
  <span class="percentile">92nd</span>
  <span class="label">Percentile</span>
</div>
```

---

```css
/* Utility Colors */
--color-success:        #27ae60  /* Training, improvement, positive changes */
--color-warning:        #f59e0b  /* Warnings, caution states */
--color-error:          #e74c3c  /* Errors, critical states */
--color-info:           #3b82f6  /* Informational messages */
```

**When to Use:**
- **Success**: Training programs, completed achievements, positive deltas
- **Warning**: Data limitations, incomplete profiles
- **Error**: API failures, validation errors
- **Info**: Tooltips, help text

---

### Border Colors

```css
--color-border-light:   #f5f5f7  /* Subtle dividers */
--color-border:         #e5e5e7  /* Default borders */
--color-border-dark:    #d1d1d6  /* Emphasis borders */
--color-border-darker:  #3a3a3a  /* Dark theme borders */
```

**Border Width Standards:**
- Subtle: `1px solid var(--color-border-light)`
- Default: `2px solid var(--color-border)`
- Emphasis: `3px solid var(--color-primary)`
- Strong: `4px solid var(--color-primary)`

---

## Typography

### Font Families

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
--font-mono: 'Roboto Mono', 'Courier New', monospace;
```

**Usage:**
- **Sans (Inter)**: 95% of all text (body, headings, UI)
- **Mono (Roboto Mono)**: Lap times, technical data, code

---

### Font Sizes

| Token | Size | Weight | Line Height | Letter Spacing | Use Case |
|-------|------|--------|-------------|----------------|----------|
| `text-display` | 48px | 900 | 1.0 | -1.5px | Hero sections, landing pages |
| `text-h1` | 32px | 800 | 1.2 | -1.0px | Page titles |
| `text-h2` | 24px | 700 | 1.3 | -0.5px | Section headers |
| `text-h3` | 20px | 700 | 1.4 | -0.3px | Card titles, subsections |
| `text-h4` | 16px | 600 | 1.4 | 0 | Small headers |
| `text-body-lg` | 16px | 500 | 1.6 | 0 | Primary body text |
| `text-body` | 14px | 500 | 1.6 | 0 | Secondary body text |
| `text-body-sm` | 13px | 500 | 1.5 | 0 | Tertiary text |
| `text-caption` | 12px | 600 | 1.4 | 0.5px | Labels, metadata |
| `text-overline` | 11px | 700 | 1.4 | 1.0px | Uppercase labels, tags |
| `text-stat` | 36px | 900 | 1.0 | -0.5px | Key metric values |
| `text-stat-lg` | 48px | 900 | 1.0 | -1.0px | Hero stats |

### Font Weights

```css
--font-normal:     400
--font-medium:     500  /* Body text, paragraphs */
--font-semibold:   600  /* Emphasis, labels */
--font-bold:       700  /* Headings, buttons */
--font-extrabold:  800  /* Major headings */
--font-black:      900  /* Stats, numbers, display text */
```

**Weight Guidelines:**
- **400-500**: Body text, descriptions
- **600**: Labels, secondary headings
- **700**: Primary headings, buttons, tabs
- **800**: Page titles (H1)
- **900**: Stats, metrics, driver numbers

---

### Typography Examples

```css
/* Page Title */
.page-title {
  font-family: var(--font-sans);
  font-size: 32px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -1px;
  color: var(--color-text-primary);
}

/* Section Header */
.section-header {
  font-family: var(--font-sans);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.5px;
  color: var(--color-text-primary);
}

/* Card Title */
.card-title {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.3px;
  color: var(--color-text-primary);
}

/* Body Text */
.body-text {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

/* Label */
.label {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

/* Stat Value */
.stat-value {
  font-family: var(--font-sans);
  font-size: 36px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.5px;
  color: var(--color-primary);
}
```

---

## Spacing

### 8pt Grid System

All spacing should be multiples of 4px (0.25rem):

| Token | Value | Use Case |
|-------|-------|----------|
| `spacing-1` | 4px | Minimal internal padding |
| `spacing-2` | 8px | Tight gaps between elements |
| `spacing-3` | 12px | Small gaps |
| `spacing-4` | 16px | Default gap |
| `spacing-5` | 20px | Medium gap |
| `spacing-6` | 24px | Standard section gap |
| `spacing-8` | 32px | Large section gap |
| `spacing-10` | 40px | Extra large section gap |
| `spacing-12` | 48px | Major section break |
| `spacing-16` | 64px | Page-level spacing |

### Spacing Patterns

**Card Padding:**
```css
/* Small card */
padding: 20px;

/* Medium card (default) */
padding: 24px;

/* Large card */
padding: 32px;
```

**Section Gaps:**
```css
/* Between cards */
gap: 24px;

/* Between major sections */
gap: 32px;

/* Between page sections */
gap: 48px;
```

**Page Container:**
```css
/* Desktop */
padding: 40px 60px;

/* Tablet */
padding: 32px 40px;

/* Mobile */
padding: 24px;
```

---

## Layout & Structure

### Container Max-Widths

```css
--container-max-width: 1400px  /* Standard page container */
--container-narrow:    1200px  /* Narrow content (articles, forms) */
--container-wide:      1600px  /* Wide dashboards (if needed) */
```

**Why 1400px?**
- Optimal for 1920x1080 screens (most common resolution)
- Leaves 260px breathing room on each side
- Content doesn't stretch to infinity on ultrawide monitors
- Still feels spacious, not cramped

**Usage:**
```css
.page-container {
  max-width: var(--container-max-width);
  margin: 0 auto;
}
```

---

### Grid System

**2-Column Layout:**
```css
.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .grid-2col {
    grid-template-columns: 1fr;
  }
}
```

**3-Column Layout:**
```css
.grid-3col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

@media (max-width: 1200px) {
  .grid-3col {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .grid-3col {
    grid-template-columns: 1fr;
  }
}
```

**Auto-Fill Grid (Cards):**
```css
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}
```

---

## Borders & Shadows

### Border Widths

```css
--border-subtle:   1px
--border-default:  2px
--border-emphasis: 3px
--border-strong:   4px
--border-hero:     5px  /* Use sparingly */
```

### Border Radius

```css
--radius-sm:  4px   /* Small elements (tags, badges) */
--radius:     8px   /* Default (buttons, inputs) */
--radius-md:  12px  /* Medium cards */
--radius-lg:  16px  /* Large cards */
--radius-xl:  20px  /* Hero sections */
--radius-full: 9999px /* Circles, pills */
```

### Box Shadows

```css
/* Subtle elevation */
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.08);

/* Default card shadow */
--shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

/* Hover state shadow */
--shadow-lg: 0 8px 24px rgba(235, 10, 30, 0.2);

/* Strong emphasis */
--shadow-xl: 0 12px 48px rgba(235, 10, 30, 0.3);
```

**Usage:**
```css
/* Resting state */
.card {
  box-shadow: var(--shadow);
  transition: box-shadow 200ms ease;
}

/* Hover state */
.card:hover {
  box-shadow: var(--shadow-lg);
}
```

---

## Animations & Transitions

### Timing

```css
--duration-fast:    150ms  /* Hover state changes, color transitions */
--duration-default: 200ms  /* Button clicks, card hovers */
--duration-slow:    300ms  /* Layout shifts, expansions */
```

### Easing Functions

```css
--ease-default:  ease
--ease-in:       ease-in
--ease-out:      ease-out
--ease-in-out:   ease-in-out
--ease-smooth:   cubic-bezier(0.4, 0, 0.2, 1)  /* Material Design easing */
```

### Standard Transitions

```css
/* All properties (use sparingly) */
transition: all 200ms ease;

/* Specific properties (preferred) */
transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;

/* Transform only */
transition: transform 200ms ease;

/* Shadow only */
transition: box-shadow 200ms ease;
```

---

## Component-Specific Tokens

### Buttons

```css
/* Button sizing */
--btn-padding-sm:  8px 16px
--btn-padding-md:  12px 24px
--btn-padding-lg:  16px 32px

/* Button font sizes */
--btn-font-sm:  13px
--btn-font-md:  14px
--btn-font-lg:  16px

/* Button heights */
--btn-height-sm:  36px
--btn-height-md:  44px
--btn-height-lg:  52px
```

---

### Driver Number Badges

```css
/* Hero badge (page headers) */
--badge-hero-size:   140px
--badge-hero-font:   70px
--badge-hero-border: 5px

/* Card badge (driver cards) */
--badge-card-size:   48px
--badge-card-font:   24px
--badge-card-border: 3px

/* Table badge (rankings table) */
--badge-table-size:   36px
--badge-table-font:   18px
--badge-table-border: 3px
```

---

### Stat Cards

```css
/* Card structure */
--stat-card-padding:      24px
--stat-card-border:       4px
--stat-card-radius:       12px

/* Typography */
--stat-card-value-size:   36px
--stat-card-label-size:   12px
--stat-card-title-size:   16px
```

---

## Responsive Breakpoints

```css
--breakpoint-mobile:  768px
--breakpoint-tablet:  1024px
--breakpoint-desktop: 1440px
--breakpoint-wide:    1920px
```

**Usage:**
```css
/* Mobile-first approach */
.element {
  padding: 24px;
}

@media (min-width: 768px) {
  .element {
    padding: 32px 40px;
  }
}

@media (min-width: 1024px) {
  .element {
    padding: 40px 60px;
  }
}
```

---

## Z-Index Scale

```css
--z-base:       0    /* Normal content */
--z-dropdown:   100  /* Dropdowns, tooltips */
--z-sticky:     200  /* Sticky headers */
--z-fixed:      300  /* Fixed navigation */
--z-overlay:    400  /* Modal overlays */
--z-modal:      500  /* Modals, dialogs */
--z-toast:      600  /* Toasts, notifications */
--z-tooltip:    700  /* Always on top tooltips */
```

---

## Usage Examples

### Complete Card Component

```css
.driver-card {
  /* Layout */
  padding: 24px;
  max-width: 400px;

  /* Colors */
  background: var(--color-bg-white);
  border: 4px solid var(--color-border);

  /* Border & Shadow */
  border-radius: 16px;
  box-shadow: var(--shadow);

  /* Animation */
  transition: all 200ms ease;
}

.driver-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.driver-card-title {
  /* Typography */
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.3px;

  /* Color */
  color: var(--color-text-primary);

  /* Spacing */
  margin-bottom: 12px;
}

.driver-card-stat {
  /* Typography */
  font-family: var(--font-sans);
  font-size: 36px;
  font-weight: 900;
  line-height: 1;

  /* Color */
  color: var(--color-primary);
}
```

---

### Complete Button Component

```css
.btn-primary {
  /* Layout */
  padding: 12px 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  /* Typography */
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  /* Colors */
  background: var(--color-primary);
  color: #ffffff;
  border: none;

  /* Border & Shadow */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(235, 10, 30, 0.3);

  /* Interaction */
  cursor: pointer;
  transition: background-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(235, 10, 30, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Implementation Checklist

When creating new components or pages:

- [ ] Use design tokens, not hardcoded values
- [ ] Typography follows the defined scale
- [ ] Colors come from the palette (no random colors)
- [ ] Spacing uses 8pt grid (multiples of 4px)
- [ ] Borders use standard widths (2px, 3px, 4px)
- [ ] Border radius uses standard values
- [ ] Transitions use standard timing (150ms, 200ms, 300ms)
- [ ] Shadows use predefined shadows
- [ ] Responsive breakpoints match standards
- [ ] Z-index comes from the scale

---

**Last Updated:** November 10, 2025
**Version:** 1.0
**Status:** Draft for Review
