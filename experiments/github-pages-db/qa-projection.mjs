// Reuse the QA fields already carried by the cross-database index.
export function qaFromSearchRow(row) {
  if (!Array.isArray(row.fields) || row.fields.length !== 6) throw new Error("Invalid Q&A projection");
  return {
    id: row.id, service_code: row.serviceCode, service_label: row.serviceLabel,
    scope: row.scope, current_service_scope: row.currentServiceScope,
    standard_label: row.fields[4].value, topic: row.fields[2].value,
    question: row.fields[0].value, answer: row.fields[1].value,
    issued_source: row.issuedSource, number: row.number,
  };
}
