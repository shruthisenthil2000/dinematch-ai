---
name: Vibrant Culinary Experience
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1b1b'
  on-surface-variant: '#5b403f'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7b5800'
  on-secondary: '#ffffff'
  secondary-container: '#f9b500'
  on-secondary-container: '#684a00'
  tertiary: '#0051d4'
  on-tertiary: '#ffffff'
  tertiary-container: '#2f6bf3'
  on-tertiary-container: '#fefcff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdea6'
  secondary-fixed-dim: '#ffbb0c'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5d4200'
  tertiary-fixed: '#dbe1ff'
  tertiary-fixed-dim: '#b3c5ff'
  on-tertiary-fixed: '#00174a'
  on-tertiary-fixed-variant: '#003ea7'
  background: '#fcf9f8'
  on-background: '#1b1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: beVietnamPro
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
  display-md:
    fontFamily: beVietnamPro
    fontSize: 36px
    fontWeight: '800'
    lineHeight: '1.2'
  headline-lg:
    fontFamily: beVietnamPro
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.3'
  headline-md:
    fontFamily: beVietnamPro
    fontSize: 22px
    fontWeight: '700'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: beVietnamPro
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: beVietnamPro
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: beVietnamPro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: beVietnamPro
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-lg:
    fontFamily: beVietnamPro
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  label-md:
    fontFamily: beVietnamPro
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.03em
  label-sm:
    fontFamily: beVietnamPro
    fontSize: 10px
    fontWeight: '700'
    lineHeight: '1.1'
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
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 20px
  margin: 24px
---

## Brand & Style

The design system is engineered to evoke hunger, excitement, and reliability. It centers on a "Food-First" philosophy, where the interface acts as a high-clarity window into culinary offerings. The brand personality is high-energy and approachable, balancing the urgency of food delivery with the curated feel of restaurant discovery.

The visual style follows a **Modern Corporate** aesthetic with tactile influences. It prioritizes clarity through generous whitespace and utilizes high-quality photography as a primary structural element. By combining a signature high-vibrancy red with a sophisticated charcoal, the system establishes an immediate sense of brand authority while maintaining a friendly, community-focused atmosphere.

## Colors

This design system utilizes a high-contrast palette designed for legibility and brand recognition.

- **Primary Red (#E23744):** Reserved for primary actions, branding, and critical highlights. It is the "appetite trigger" of the interface.
- **Secondary Gold (#FFBA00):** Used specifically for ratings, rewards, and "Best in Class" callouts to signify quality.
- **Deep Charcoal (#1C1C1C):** The primary color for typography and iconography, providing a grounded contrast against light backgrounds.
- **Background Tones:** A progression of clean whites (#FFFFFF) for surfaces and ultra-light grays (#F8F8F8) for section backgrounds to create subtle containment without visual noise.

## Typography

The design system employs **beVietnamPro** to achieve an approachable yet modern tone. The typographic scale is optimized for rapid scanning, essential for users browsing through restaurant names and menus.

Headlines use heavy weights (700-800) to create a strong information hierarchy and "pop" against food imagery. Body text is set with generous line heights to ensure long menus remain readable. Label styles are frequently used in uppercase or with slight letter spacing for metadata like "DELIVERY TIME" or "OPEN NOW" to distinguish them from descriptive body text.

## Layout & Spacing

The layout is built on a **12-column fixed grid** for desktop environments (max-width 1280px) and a fluid grid for mobile devices. The rhythm of the design system is governed by an 8px base unit.

- **Grid:** Use a 20px gutter to provide breathing room between restaurant cards.
- **Margins:** Page-level margins are set to a minimum of 24px on mobile and scale up to 80px on large desktops.
- **Stacking:** Elements within a card (e.g., dish name, price, description) follow a tight 4px or 8px vertical spacing to maintain proximity, while distinct sections of the app (e.g., "Trending Near You" and "Top Brands") are separated by 48px to 80px to define clear content blocks.

## Elevation & Depth

Hierarchy is established through **Ambient Shadows** and **Tonal Layering**. The design system avoids harsh borders in favor of soft, diffused shadows that suggest objects are resting gently on the background surface.

- **Low Elevation:** Used for stationary cards and inputs. A very soft, 10% opacity charcoal shadow with a 4px blur.
- **Medium Elevation:** Used for hover states on restaurant cards and dropdown menus. The shadow expands to a 12px blur with 12% opacity.
- **High Elevation:** Reserved for floating action buttons (e.g., "View Cart") and modals. These use a multi-layered shadow to simulate significant distance from the base surface.
- **Containment:** Section headers often use a subtle bottom border (1px, #EFEEF1) instead of shadows to keep the interface feeling flat and modern.

## Shapes

The shape language is consistently **Rounded**, reflecting the friendly and organic nature of food. 

Standard components like buttons and input fields use a 0.5rem (8px) radius. Large containers, such as restaurant cards and promotional banners, utilize a 1rem (16px) radius to soften the layout. Icons and small tags (like "Veg/Non-Veg" indicators) should maintain this roundedness to ensure a cohesive visual language. Interactive elements should never have sharp 0px corners.

## Components

The components within this design system are designed to be high-contrast and highly interactive.

- **Buttons:** Primary buttons are solid Zomato Red with white text, featuring a subtle lift on hover. Secondary buttons use a charcoal outline or a light gray fill.
- **Restaurant Cards:** The hero of the discovery experience. They feature a top-heavy layout with high-quality imagery (16px radius), followed by a 12px padding area for the restaurant name (Headline-sm) and rating (Gold badge).
- **Chips:** Used for cuisine filtering (e.g., "Pizza," "Healthy"). They feature a light gray background that shifts to the primary red with white text when selected.
- **Input Fields:** Search bars are oversized with a 0.5rem radius, using a subtle shadow rather than a heavy border to invite interaction.
- **Progressive Disclosure:** Use "Dish Item" components with a small square "Add" button that transforms into a quantity selector (+/-) upon the first interaction.
- **Status Indicators:** Use small, vibrant dots for "Live Tracking" and rounded labels for "Promoted" or "Discount" tags.