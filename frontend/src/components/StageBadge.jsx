const STAGE_COLORS = {
  Applied: "stage-applied",
  R1: "stage-progress",
  R2: "stage-progress",
  R3: "stage-progress",
  Approved: "stage-approved",
  Reject: "stage-rejected",
  "R1 Reject": "stage-rejected",
  "R2 Reject": "stage-rejected",
  "R3 Reject": "stage-rejected",
};

export default function StageBadge({ stage }) {
  const cls = STAGE_COLORS[stage] || "stage-applied";
  return <span className={`badge ${cls}`}>{stage}</span>;
}
