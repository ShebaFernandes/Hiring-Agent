// Mirrors backend/app/constants.py STAGES. Kept as a small static list here
// rather than fetched from /api/stages, since it changes rarely and this
// avoids an extra network round trip before the dashboard can render.
export const STAGES = [
  "Applied",
  "R1",
  "R1 Reject",
  "R2",
  "R2 Reject",
  "R3",
  "R3 Reject",
  "Approved",
  "Reject",
];
