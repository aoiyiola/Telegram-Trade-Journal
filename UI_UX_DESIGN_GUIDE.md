# UI/UX Design Guide — Trading Journal Dashboard

This document covers two things:

1. **Recommended AI-powered design tools** for prototyping and editing app UI/UX before writing code.
2. **The built-in Theme Customiser** that ships with the dashboard, which lets any user tweak and save the look-and-feel without touching code.

---

## 1. Recommended AI Design Tools

The tools below all support AI-assisted UI generation, real-time editing, and the ability to export or save a design before handing it off to developers.

| Tool | Best For | AI Features | Save & Export |
|------|----------|-------------|---------------|
| **[Figma](https://figma.com)** + plugins (Genius, Magician, Builder.io) | Collaborative wireframes and high-fidelity mockups | AI component generation, auto-layout suggestions | Figma cloud save, export to PNG/SVG/CSS |
| **[v0.dev](https://v0.dev)** (Vercel) | React/Tailwind UI generation from prompts | Generates full JSX from natural-language descriptions | Copy code or download as a project |
| **[Framer](https://framer.com)** | Interactive prototypes with live animations | AI-generated layouts; breakpoint-aware design | Framer cloud + publish or export HTML |
| **[Uizard](https://uizard.io)** | Rapid wireframe → hi-fi mockup from sketches or text | Sketch-to-UI, theme generation | Download images or share link |
| **[Galileo AI](https://usegalileo.ai)** | High-fidelity UI generation from text prompts | Full-screen UI from a single sentence | Export Figma-compatible frames |
| **[Penpot](https://penpot.app)** *(open source)* | Self-hosted alternative to Figma | AI plugins via community | SVG/CSS export; self-hosted saves |

### Recommended Workflow

```
1. Describe the app concept in Galileo AI or v0.dev to get a starting point quickly.
2. Refine the result in Figma (import via the Builder.io plugin) or edit directly in v0.dev.
3. Save the design file / share a Figma link with your team before any coding begins.
4. Use the exported Tailwind classes or CSS variables from the design tool to match the
   dashboard's existing token-based theming system (see Section 2 below).
```

---

## 2. Built-in Theme Customiser

The dashboard ships with a **Theme Customiser** accessible from the top-right of every page.  
No design tool or code knowledge is required.

### Features

- **5 preset themes** — Dark Blue (default), Dark Green, Dark Purple, Dark Amber, Midnight.
- **Custom accent colour** — a colour picker lets you override the accent for any preset.
- **Persistent saves** — selections are stored in `localStorage` and restored on every visit.
- **One-click reset** — restores the default Dark Blue theme instantly.

### How to Use

1. Open the dashboard in a browser.
2. Click the **palette icon** (🎨) in the header.
3. Pick a preset theme or select a custom accent colour.
4. Your choice is saved automatically — no submit button needed.
5. Share the URL with a team-mate; they will see your chosen theme on their device too  
   (because the preference is stored locally, each user has their own saved setting).

### Theme Token Reference

The theming system uses CSS custom properties on `:root`.  
These tokens are set by `src/hooks/useTheme.js` and can be referenced anywhere in the app.

| Token | Purpose |
|-------|---------|
| `--color-bg-primary` | Page / outermost background |
| `--color-bg-secondary` | Cards, sidebar, header |
| `--color-bg-tertiary` | Hover states, inner panels |
| `--color-border` | All borders and dividers |
| `--color-accent` | Buttons, links, highlighted text |
| `--color-accent-hover` | Hover state for accent elements |
| `--color-text` | Primary body text |
| `--color-text-muted` | Secondary / helper text |

### Adding a New Preset

Open `src/hooks/useTheme.js` and append an entry to the `PRESET_THEMES` array:

```js
{
  id: 'my-theme',
  name: 'My Theme',
  description: 'Custom dark theme with rose accents',
  colors: {
    bgPrimary:    '#1a0010',
    bgSecondary:  '#2d0018',
    bgTertiary:   '#3d0020',
    border:       '#6d0036',
    accent:       '#fb7185',
    accentHover:  '#f43f5e',
    text:         '#fff1f2',
    textMuted:    '#fda4af',
  },
},
```

The new theme will appear immediately in the customiser panel without any other changes.
