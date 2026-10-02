# Power BI preparation

No `.pbix` file is included. Use PostgreSQL view `vw_monthly_sales` plus the Gold exports as the source. Recommended relationships are dimensions to `fact_sales` by surrogate keys. Measures: `Revenue = SUM(fact_sales[revenue])`, `Profit = SUM(fact_sales[profit])`, and `AOV = DIVIDE([Revenue], DISTINCTCOUNT(fact_sales[date_key]))`. Build pages for executive KPIs, monthly/state sales, inventory alerts, and pipeline quality.
