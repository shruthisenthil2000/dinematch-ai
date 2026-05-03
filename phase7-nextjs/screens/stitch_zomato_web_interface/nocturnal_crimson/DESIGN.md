---
name: Nocturnal Crimson
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#c6c6c7'
  on-secondary: '#2f3131'
  secondary-container: '#454747'
  on-secondary-container: '#b4b5b5'
  tertiary: '#c8c6c5'
  on-tertiary: '#313030'
  tertiary-container: '#929090'
  on-tertiary-container: '#2a2a29'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474646'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  h1:
    fontFamily: Be Vietnam Pro
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Be Vietnam Pro
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h3:
    fontFamily: Be Vietnam Pro
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.5'
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
  label-caps:
    fontFamily: Be Vietnam Pro
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin: 20px
---

## Brand & Style

This design system establishes a premium, late-night aesthetic tailored for high-end food discovery and seamless delivery. The personality is sophisticated, confident, and appetizing. By utilizing a deep charcoal foundation, the signature brand red is empowered to act as a high-visibility beacon for conversion and navigation.

The visual style is **Modern Corporate** with a heavy lean into **Minimalism**. It prioritizes content—specifically food photography—by reducing UI clutter. Depth is achieved not through heavy gradients, but through a structured system of tonal layering and precise, razor-thin borders that define the architecture of the interface without sacrificing the "infinite" feel of the dark canvas.

## Colors

The palette is anchored by the "True Dark" background (#0a0a0a) to ensure OLED efficiency and maximum contrast. The secondary "Surface" color (#121212) provides the first level of elevation for containers and list items.

Signature Red (#E23744) is reserved strictly for primary calls-to-action, active states, and brand-critical highlights. It should never be used for large background areas, preserving its impact. Functional colors for success, warning, and error should be desaturated to harmonize with the dark environment while remaining legible. Text colors transition from pure white for headings to a muted light grey for metadata to establish a clear information hierarchy.

## Typography

This design system utilizes **Be Vietnam Pro** across all touchpoints to maintain a contemporary and approachable feel. Headlines use Bold (700) weights with slightly tightened letter-spacing to create a "locked-in" editorial look. 

Body text is optimized for readability against dark backgrounds; Semi-Bold (600) is used for emphasis within paragraphs rather than standard Bold to prevent "blooming" or visual vibration. Labels and secondary metadata utilize a lighter grey color and the "label-caps" style to differentiate functional text from narrative content.

## Layout & Spacing

The layout follows a **Fluid Grid** model based on an 8px rhythmic scale. For mobile views, a standard 4-column grid is used with 16px gutters and 20px side margins to ensure content does not feel cramped against the bezel.

Spacing is used to group related items—smaller increments (4px, 8px) are reserved for internal component spacing (e.g., text to icon), while larger increments (24px, 32px) are used to separate distinct content sections or restaurant categories. Consistency in these vertical rhythms is essential to maintain the "Sophisticated" brand promise.

## Elevation & Depth

Depth in this design system is conveyed through **Tonal Layers** and **Subtle Outlines**. 
1. **Base Layer (#0a0a0a):** Used for the main application background.
2. **Surface Layer (#121212):** Used for cards, sheets, and persistent navigation bars.
3. **Overlay Layer (#1e1e1e):** Used for tooltips, menus, and modals.

To compensate for the low contrast between dark tones, every elevated card must feature a 1px solid border using a low-opacity white (rgba(255, 255, 255, 0.08)). Shadows should be "Ambient"—highly diffused, using a black tint with a large blur radius (16px to 24px) and 40% opacity to create a soft glow effect rather than a harsh drop-shadow.

## Shapes

The shape language for this design system is **Rounded**, striking a balance between the organic nature of food and the precision of a high-tech platform. 

- **Standard Elements (Buttons, Inputs):** 0.5rem (8px) radius.
- **Content Containers (Restaurant Cards, Banners):** 1rem (16px) radius to create a soft, inviting frame for food photography.
- **Search Bars & Tags:** Full pill-shape (circular ends) to indicate high interactivity and ease of use.

## Components

### Buttons
Primary buttons use the signature #E23744 background with white text. Secondary buttons utilize the #121212 surface color with a subtle white border. Ghost buttons are reserved for "Less Important" actions like "View More Details."

### Cards
Cards are the primary vehicle for restaurant listings. They feature a #121212 background, the 1px subtle border defined in Elevation, and a 16px corner radius. Images within cards should have a subtle dark-to-transparent gradient overlay at the bottom to ensure white text overlays remain legible.

### Input Fields
Inputs use a #121212 fill with an 8px radius. The border remains #1e1e1e in a resting state and transitions to the signature #E23744 when focused. Placeholder text should be a mid-tone grey to ensure it is clearly distinguishable from user input.

### Chips & Tags
Used for cuisine types or filters. These should be pill-shaped. Active chips use a semi-transparent red background (15% opacity) with a solid red border and text to indicate selection without over-powering the visual field.

### Selection Controls
Checkboxes and Radio buttons use #E23744 for the active state. In the inactive state, they should be defined by a simple 1.5px light grey outline.