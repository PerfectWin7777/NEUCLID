/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{html,ts}",
    ],
    theme: {
        extend: {
            colors: {
                'neuclid-bg': '#09090b',      // Noir profond (fond canvas)
                'neuclid-ui': '#18181b',      // Gris anthracite (panneaux)
                'neuclid-border': '#27272a',  // Bordures subtiles
                'neuclid-accent': '#3b82f6',  // Bleu Neuclid
            }
        },
    },
    plugins: [],
}