# Requirements Document

## Introduction

This document defines the requirements for adding a dark mode toggle to the Apex-Mart single-page application. The site is a vanilla HTML/CSS/JS SPA served by FastAPI. It uses CSS custom properties (`--bg`, `--ink`, `--muted`, `--card`, `--line`, `--brand`, `--brand-2`, `--good`, `--warn`, `--danger`) defined in `:root` to control the visual theme. The toggle must switch between a light and dark colour palette, persist the user's choice across sessions via `localStorage`, and honour the user's OS-level colour-scheme preference on first visit.

---

## Glossary

- **Toggle_Button**: The interactive UI control placed in the page header that the user clicks to switch between light and dark mode.
- **Theme_Manager**: The JavaScript module responsible for reading, applying, and persisting the active theme.
- **Theme**: One of two named states — `light` or `dark` — that maps to a distinct set of CSS custom-property values.
- **CSS_Variables**: The set of `:root` custom properties (`--bg`, `--ink`, `--muted`, `--card`, `--line`, `--brand`, `--brand-2`, `--good`, `--warn`, `--danger`) that control all colours in the application.
- **localStorage**: The browser's `localStorage` Web Storage API used to persist the user's theme preference.
- **OS_Preference**: The colour-scheme preference reported by the browser via the `prefers-color-scheme` media query.
- **Dark_Palette**: The set of CSS custom-property values used when the dark theme is active (dark background, light text, adjusted surface colours).
- **Light_Palette**: The default set of CSS custom-property values corresponding to the existing light design.
- **ARIA_Label**: The `aria-label` attribute on the Toggle_Button that communicates the current action to assistive technology.
- **Header_Action_Group**: The `<div style="display:flex; gap:8px;">` container in the header's right side that holds the hamburger button and the cart button (`#cartHeaderBtn`).

---

## Requirements

### Requirement 1: Theme Switching via Toggle Button

**User Story:** As a user, I want a toggle button in the header, so that I can switch between the light and dark themes at any time while browsing the site.

#### Acceptance Criteria

1. THE Toggle_Button SHALL be rendered inside the Header_Action_Group, immediately to the left of the cart button (`#cartHeaderBtn`), and SHALL be visible on all views (Analytics, Shop, Search/Lab).
2. WHEN the user clicks the Toggle_Button while the light theme is active, THE Theme_Manager SHALL apply the dark theme to the page.
3. WHEN the user clicks the Toggle_Button while the dark theme is active, THE Theme_Manager SHALL apply the light theme to the page.
4. WHEN the Theme_Manager applies a theme, THE CSS_Variables on `:root` SHALL update to the corresponding palette values within 100 ms of the click event.
5. THE Toggle_Button SHALL display a sun icon (☀️ or equivalent SVG) when the dark theme is active and a moon icon (🌙 or equivalent SVG) when the light theme is active.

---

### Requirement 2: Dark Colour Palette

**User Story:** As a user, I want the dark theme to use a comfortable, low-brightness colour scheme, so that I can use the app in low-light environments without eye strain.

#### Acceptance Criteria

1. WHEN the dark theme is active, THE CSS_Variables SHALL use the following Dark_Palette values:
   - `--bg`: `#0f172a`
   - `--ink`: `#f1f5f9`
   - `--muted`: `#94a3b8`
   - `--card`: `#1e293b`
   - `--line`: `#334155`
2. WHEN the dark theme is active, THE CSS_Variables `--brand`, `--brand-2`, `--good`, `--warn`, and `--danger` SHALL retain the same values as the Light_Palette to preserve semantic colour meaning.
3. WHEN the dark theme is active, THE header `background` and hardcoded `#fff` / `#f8fafc` surface colours that are not controlled by CSS_Variables SHALL be overridden by a `[data-theme="dark"]` CSS selector so all surfaces match the Dark_Palette.

---

### Requirement 3: Preference Persistence

**User Story:** As a user, I want my chosen theme to be remembered, so that I do not have to re-select it every time I reload or revisit the page.

#### Acceptance Criteria

1. WHEN the user activates a theme, THE Theme_Manager SHALL write the theme name (`"light"` or `"dark"`) to `localStorage` under the key `"apex-theme"`.
2. WHEN the page loads, THE Theme_Manager SHALL read the `"apex-theme"` key from `localStorage` and apply the stored theme before the first paint.
3. IF the `"apex-theme"` key is absent from `localStorage`, THEN THE Theme_Manager SHALL apply the theme that matches the OS_Preference reported by `prefers-color-scheme`.
4. IF the `"apex-theme"` key is absent from `localStorage` and the OS_Preference is also unavailable, THEN THE Theme_Manager SHALL apply the light theme by default.
5. THE Theme_Manager SHALL apply the persisted or inferred theme during the `<head>` script execution phase so that no flash of the wrong theme is visible on page load.

---

### Requirement 4: Accessibility

**User Story:** As a user relying on assistive technology, I want the toggle button to be properly labelled, so that I can understand and operate it with a screen reader or keyboard.

#### Acceptance Criteria

1. THE Toggle_Button SHALL include an `aria-label` attribute that reads `"Switch to dark mode"` when the light theme is active and `"Switch to light mode"` when the dark theme is active.
2. THE Toggle_Button SHALL be focusable via keyboard Tab navigation and SHALL be operable via the Enter and Space keys.
3. THE Toggle_Button SHALL have a minimum touch/click target size of 44 × 44 CSS pixels.
4. WHEN the theme changes, THE Toggle_Button ARIA_Label SHALL update to reflect the new toggle action within the same event handler that applies the theme.

---

### Requirement 5: No-Flash Initialisation

**User Story:** As a user, I want the correct theme to appear immediately on page load, so that I do not see a brief white flash before dark mode is applied.

#### Acceptance Criteria

1. THE Theme_Manager initialisation script SHALL be placed in a `<script>` tag in `<head>`, before any stylesheet link tags that define colour variables, OR shall use `<script>` with synchronous DOM attribute setting so it executes before the browser renders the body.
2. WHEN the Theme_Manager applies the initial theme, THE `<html>` element SHALL receive a `data-theme` attribute (`"light"` or `"dark"`) before the body is painted.
3. THE initial theme application SHALL NOT require any asynchronous operations (no `fetch`, `setTimeout`, or `Promise`).

---

### Requirement 6: Transition Animation

**User Story:** As a user, I want the theme switch to feel smooth, so that abrupt colour changes do not feel jarring.

#### Acceptance Criteria

1. THE `<body>` element CSS SHALL include a `transition` property covering `background-color` and `color` with a duration of 200 ms or less.
2. WHEN the Theme_Manager switches themes, all CSS_Variable-driven surfaces SHALL transition to their new values within 200 ms.
3. THE transition SHALL NOT apply on the initial page load so that no animation plays before the user has interacted with the page.
