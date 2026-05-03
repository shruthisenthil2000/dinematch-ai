---
name: Obsidian Gourmet
colors:
  surface: '#1e0f0f'
  surface-dim: '#1e0f0f'
  surface-bright: '#473534'
  surface-container-lowest: '#180a0a'
  surface-container-low: '#271717'
  surface-container: '#2c1b1b'
  surface-container-high: '#372625'
  surface-container-highest: '#423030'
  on-surface: '#f9dcda'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#f9dcda'
  inverse-on-surface: '#3e2c2b'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#c8c6c5'
  on-secondary: '#303030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#71d7cf'
  on-tertiary: '#003734'
  tertiary-container: '#32a099'
  on-tertiary-container: '#00302d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1c'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#8ef4eb'
  tertiary-fixed-dim: '#71d7cf'
  on-tertiary-fixed: '#00201e'
  on-tertiary-fixed-variant: '#00504c'
  background: '#1e0f0f'
  on-background: '#f9dcda'
  surface-variant: '#423030'
typography:
  display-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Be Vietnam Pro
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-base:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  ai-reasoning:
    fontFamily: Be Vietnam Pro
    fontSize: 15px
    fontWeight: '500'
    lineHeight: '1.7'
    letterSpacing: 0.01em
  label-sm:
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
  unit: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1200px
  gutter: 24px
---

## Brand & Style
This design system establishes a high-end, AI-centric aesthetic that merges the culinary energy of vibrant red accents with the clinical precision of modern glassmorphism. The brand personality is "The Discerning Concierge"—sophisticated, predictive, and exclusive. 

The visual style utilizes **Glassmorphism** as its primary vehicle for depth, employing semi-transparent obsidian layers and heavy backdrop blurs to create a sense of focused immersion. It targets tech-savvy food enthusiasts who value speed and curation. The emotional response should be one of "effortless luxury," where complex AI reasoning is presented through a clean, spacious, and highly legible interface.

## Colors
The palette is rooted in a "Deep Obsidian" foundation to ensure high contrast for AI-generated content. 

- **Primary Accent:** #E23744 (Zomato Red) is used sparingly for critical actions, status indicators, and branding moments to maintain its premium impact.
- **Base Layers:** The absolute background is #0F0F0F, while elevated surfaces use #1E1E1E.
- **Glass Layers:** Use the surface color with 70% opacity and a minimum of 20px backdrop-blur to create the signature glassmorphic effect.
- **Typography:** Pure white (#FFFFFF) is reserved for primary headers and AI reasoning snippets to maximize readability against the dark backdrop, while #A0A0A0 provides a soft hierarchy for metadata and secondary descriptions.

## Typography
This design system utilizes **Be Vietnam Pro** for its contemporary, approachable, yet geometric structure that excels in dark mode. 

The typographic scale emphasizes "AI Reasoning" snippets with slightly increased line-height and medium weights to ensure long-form explanations are comfortable to read. Headlines use a tighter letter-spacing and heavier weights to feel authoritative. All labels should be rendered in uppercase with generous tracking to provide a technical, "SaaS-startup" feel.

## Layout & Spacing
The layout follows a **fluid grid system** with a spacious 8px-based rhythm. 

- **Margins & Gutters:** Use 24px gutters to allow elements enough room to "breathe," essential for the glassmorphic style to prevent visual clutter.
- **Philosophy:** Emphasize whitespace (or "dark space") to highlight AI suggestions. Content should be centered in a 1200px max-width container for desktop, while mobile views should utilize 16px side margins. 
- **Transitions:** Layout shifts and element appearances must use smooth, 300ms cubic-bezier (0.4, 0, 0.2, 1) easing to reinforce the premium feel.

## Elevation & Depth
Depth is not communicated through traditional shadows alone, but through **Tonal Glassmorphism**.

1.  **Level 0 (Base):** #0F0F0F background.
2.  **Level 1 (Card/Surface):** #1E1E1E with a 1px subtle border (#FFFFFF at 5% opacity).
3.  **Level 2 (Active/Floating):** Surface color with 70% opacity, 20px-40px backdrop-blur, and an extra-diffused 30px shadow with a 20% opacity black tint.
4.  **AI Focus:** Elements generated by the AI should have a subtle outer glow using the Primary Accent color at 10% opacity to draw the eye without being distracting.

## Shapes
The design system adopts a **Rounded** shape language to feel modern and inviting. 

- **Cards & Containers:** Use a standard `radius_md` (16px) or `radius_lg` (24px) for main content areas.
- **Interactive Elements:** Buttons and input fields should use `radius_md` to maintain a consistent "squishy" yet professional look.
- **Pills:** Use `radius_full` for status tags (e.g., "AI Optimized", "Open Now").

## Components
- **Buttons:** Primary buttons use the `accent_gradient` with white text. Secondary buttons are ghost-style with a 1px white border at 10% opacity and a heavy backdrop-blur.
- **AI Reasoning Cards:** These cards feature a vertical 2px accent line on the left edge and a slightly lighter surface background (#252525) to differentiate AI logic from static data.
- **Input Fields:** Search and prompt bars should be oversized (height: 56px) with 16px rounding and a subtle inner glow on focus.
- **Chips/Tags:** Small, semi-transparent obsidian pills with the primary accent color used only for the text or a small leading icon.
- **Glass Overlay Panels:** Use for sidebars or "match" details; they must always include a `backdrop-filter: blur(20px)` to ensure text legibility over diverse food imagery.
- **Dynamic Progress Bars:** When the AI is "matching," use a pulsing gradient bar using the Primary Accent color.