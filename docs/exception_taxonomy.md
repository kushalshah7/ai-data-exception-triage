# Exception Taxonomy

| Category | Definition | Example |
| --- | --- | --- |
| Missing Reference Data | Required security master field is blank. | Missing ISIN blocks downstream enrichment. |
| Stale Price | Latest vendor price is older than policy. | Bloomberg close not received for three days. |
| Price Outlier | Price move breaches tolerance. | Equity close moves 38% without corporate action. |
| Trade Match Break | Trade cannot be matched to expected counterparty/source record. | Security key differs between OMS and accounting. |
| Position Reconciliation Break | Position quantity or market value differs across books. | Custodian quantity differs from IBOR. |
| Duplicate Record | Same business key appears more than once. | Duplicate trade booking. |
| Invalid Currency | Currency conflicts with security, trade, or portfolio setup. | EUR bond loaded with USD trade currency. |
| Missing Client Mapping | Client, account, or portfolio mapping is incomplete. | Portfolio code not mapped to client hierarchy. |
| Delayed Source Load | Upstream batch or feed is late. | Custodian file arrives after SLA. |
| Performance Return Outlier | Return profile is outside expected range. | Portfolio return jump caused by stale valuation. |
| Unknown / Needs SME Review | Pattern does not meet automated confidence threshold. | New issue type after vendor change. |
