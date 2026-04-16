# Targeted Missing Pull Log

Generated at: 2026-04-14T23:58:33.832754

## Summary

- Total tasks processed: 628
- Success with inserts: 139
- Confirmed missing (no rows): 489
- Failed tasks: 0

## Follow-up Note (2026-04-15)

- A dedicated 2023 remap retry was run using alternate sensor IDs per location.
- Result: 89 tasks executed, 0 inserts, 89 confirmed missing, 0 failed.
- See `data/raw/remap_2023_retry_log.md` and `data/raw/remap_2023_retry_events.parquet` for full evidence.

## Failures / Confirmed Missing

| Year | File | Station | Param | Date From | Date To | Status | HTTP | Message |
|---:|---|---|---|---|---|---|---:|---|
| 2022 | 2022.parquet | Peenya, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SaneguravaHalli - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SaneguravaHalli - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SaneguravaHalli - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SaneguravaHalli - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | City Railway Station, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Sanegurava Halli, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Sanegurava Halli, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Silk Board, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Silk Board, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hombegowda Nagar, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hombegowda Nagar, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hebbal, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hebbal, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hebbal, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Hebbal, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | blore_India_07_14_official | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SiriJaya | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | SiriJaya | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kasturi Nagar, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kasturi Nagar, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kasturi Nagar, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Shivapura_Peenya, Bengaluru - KSPCB | co | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Shivapura_Peenya, Bengaluru - KSPCB | no2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm10 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Shivapura_Peenya, Bengaluru - KSPCB | so2 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Kumaraswamy Layout | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Bellandur | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Koramangala | pm25 | 2022-01-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-01-27T00:00:00Z | 2022-01-27T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | not_inserted_all_rows_already_present_after_dedupe |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | not_inserted_all_rows_already_present_after_dedupe |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-02-07T00:00:00Z | 2022-03-24T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-06-23T00:00:00Z | 2022-07-03T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-08-04T00:00:00Z | 2022-09-12T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-10-17T00:00:00Z | 2022-10-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | co | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | co | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | no2 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm10 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | pm25 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2022 | 2022.parquet | Peenya, Bengaluru - CPCB | so2 | 2022-11-01T00:00:00Z | 2022-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SaneguravaHalli - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SaneguravaHalli - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SaneguravaHalli - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SaneguravaHalli - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - CPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - CPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - CPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - CPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - CPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Peenya, Bengaluru - CPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Sanegurava Halli, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Sanegurava Halli, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Silk Board, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Silk Board, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Silk Board, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hombegowda Nagar, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hombegowda Nagar, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hebbal, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hebbal, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hebbal, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hebbal, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | blore_India_07_14_official | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SiriJaya | pm10 | 2024-01-01T00:00:00Z | 2024-02-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SiriJaya | pm25 | 2024-01-01T00:00:00Z | 2024-02-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kasturi Nagar, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kasturi Nagar, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kasturi Nagar, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Shivapura_Peenya, Bengaluru - KSPCB | co | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Shivapura_Peenya, Bengaluru - KSPCB | no2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm10 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Shivapura_Peenya, Bengaluru - KSPCB | so2 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Kumaraswamy Layout | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Bellandur | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | Koramangala | pm25 | 2024-01-01T00:00:00Z | 2024-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SiriJaya | pm10 | 2024-03-12T00:00:00Z | 2024-03-13T23:59:59Z | confirmed_missing | 200 | not_inserted_all_rows_already_present_after_dedupe |
| 2024 | 2024.parquet | SiriJaya | pm25 | 2024-03-12T00:00:00Z | 2024-03-13T23:59:59Z | confirmed_missing | 200 | not_inserted_all_rows_already_present_after_dedupe |
| 2024 | 2024.parquet | SiriJaya | pm10 | 2024-03-17T00:00:00Z | 2024-03-19T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2024 | 2024.parquet | SiriJaya | pm25 | 2024-03-17T00:00:00Z | 2024-03-19T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - KSPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - KSPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - KSPCB | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - KSPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - KSPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - KSPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - KSPCB | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - KSPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station - KSPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station - KSPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station - KSPCB | pm10 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station - KSPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SaneguravaHalli - KSPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SaneguravaHalli - KSPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SaneguravaHalli - KSPCB | pm10 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SaneguravaHalli - KSPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | co | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | no2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm10 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | so2 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | blore_India_07_14_official | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Koramangala | pm25 | 2025-01-01T00:00:00Z | 2025-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kasturi Nagar, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kasturi Nagar, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kasturi Nagar, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Shivapura_Peenya, Bengaluru - KSPCB | co | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Shivapura_Peenya, Bengaluru - KSPCB | no2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm10 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Shivapura_Peenya, Bengaluru - KSPCB | so2 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kumaraswamy Layout | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bellandur | pm25 | 2025-01-15T00:00:00Z | 2025-02-10T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | co | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm10 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kumaraswamy Layout | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bellandur | pm25 | 2025-12-16T00:00:00Z | 2025-12-25T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Peenya, Bengaluru - CPCB | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | co | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm10 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | SiriJaya | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Kumaraswamy Layout | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2025 | 2025.parquet | Bellandur | pm25 | 2025-12-29T00:00:00Z | 2025-12-29T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Peenya, Bengaluru - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Peenya, Bengaluru - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Peenya, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Peenya, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | City Railway Station - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | City Railway Station - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | City Railway Station - KSPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | City Railway Station - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SaneguravaHalli - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SaneguravaHalli - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SaneguravaHalli - KSPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SaneguravaHalli - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Peenya, Bengaluru - CPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Silk Board, Bengaluru - KSPCB | co | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | blore_India_07_14_official | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SiriJaya | pm10 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | SiriJaya | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Bellandur | pm25 | 2026-01-01T00:00:00Z | 2026-03-30T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Kumaraswamy Layout | pm25 | 2026-01-07T00:00:00Z | 2026-01-18T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Koramangala | pm25 | 2026-01-07T00:00:00Z | 2026-01-18T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Kumaraswamy Layout | pm25 | 2026-02-20T00:00:00Z | 2026-02-23T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Koramangala | pm25 | 2026-02-20T00:00:00Z | 2026-02-23T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Kumaraswamy Layout | pm25 | 2026-02-28T00:00:00Z | 2026-02-28T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Koramangala | pm25 | 2026-02-28T00:00:00Z | 2026-02-28T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Kumaraswamy Layout | pm25 | 2026-03-10T00:00:00Z | 2026-03-16T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2026 | 2026_partial.parquet | Koramangala | pm25 | 2026-03-10T00:00:00Z | 2026-03-16T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SaneguravaHalli - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SaneguravaHalli - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SaneguravaHalli - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SaneguravaHalli - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BWSSB Kadabesanahalli, Bengaluru - CPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - CPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - CPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - CPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - CPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | BTM Layout, Bengaluru - CPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | City Railway Station, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - CPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - CPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - CPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - CPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Peenya, Bengaluru - CPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Sanegurava Halli, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Sanegurava Halli, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Sanegurava Halli, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Sanegurava Halli, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Jayanagar 5th Block, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bapuji Nagar, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bapuji Nagar, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bapuji Nagar, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bapuji Nagar, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Silk Board, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Silk Board, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Silk Board, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Silk Board, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Silk Board, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hombegowda Nagar, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hombegowda Nagar, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hombegowda Nagar, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hombegowda Nagar, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hebbal, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hebbal, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hebbal, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hebbal, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Hebbal, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | blore_India_07_14_official | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SiriJaya | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | SiriJaya | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | RVCE-Mailasandra, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kasturi Nagar, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kasturi Nagar, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kasturi Nagar, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kasturi Nagar, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Shivapura_Peenya, Bengaluru - KSPCB | co | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Shivapura_Peenya, Bengaluru - KSPCB | no2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm10 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Shivapura_Peenya, Bengaluru - KSPCB | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Shivapura_Peenya, Bengaluru - KSPCB | so2 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Kumaraswamy Layout | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Bellandur | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |
| 2023 | 2023.parquet | Koramangala | pm25 | 2023-01-01T00:00:00Z | 2023-12-31T23:59:59Z | confirmed_missing | 200 | api_returned_no_rows_for_requested_window |