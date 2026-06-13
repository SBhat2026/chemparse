// Wire these to your environment. Vite exposes VITE_* vars at build time.
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Stripe hosted Payment Link. Configure its success URL to redirect back here
// with ?paid=1 so the stateless unlock in App.jsx fires. e.g.
//   https://chemparse.app/?paid=1
export const STRIPE_PAYMENT_LINK =
  import.meta.env.VITE_STRIPE_LINK || "https://buy.stripe.com/test_PLACEHOLDER";
