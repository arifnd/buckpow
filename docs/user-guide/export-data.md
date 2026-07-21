# Export Data

Export measurement data as CSV or Excel files with date range filtering.

---

## Overview

BuckPow lets you export measurement data for external analysis in spreadsheet software, data science tools, or custom scripts. Two export formats are available:

- **CSV** — Universal format, works with any spreadsheet or data tool
- **XLSX** — Excel format with formatted headers and auto-sized columns

<!-- TODO: Replace with export buttons screenshot -->

## Measurements Page

Navigate to **Measurements** in the sidebar to view and export data.

### Page Layout

| Section | Description |
|---------|-------------|
| **Filters** | Device, session, date range |
| **Table** | Paginated measurement data |
| **Export Buttons** | CSV and XLSX download |

<!-- TODO: Replace with measurements page screenshot -->

## Filtering Data

Before exporting, use the filters to select the data you need.

### Device Filter

Select a specific device or leave blank for all devices:

| Option | Description |
|--------|-------------|
| **All** | Include measurements from all devices |
| **Specific device** | Only measurements from the selected device |

### Session Filter

Select a specific session or leave blank for all sessions:

| Option | Description |
|--------|-------------|
| **All** | Include all measurements (with or without session) |
| **Specific session** | Only measurements from the selected session |

### Date Range Filter

Use the date picker to set a start and end date:

| Field | Description |
|-------|-------------|
| **From** | Start date (inclusive) |
| **To** | End date (inclusive) |

<!-- TODO: Replace with date picker screenshot -->

!!! tip "Date format"
    Dates are in `YYYY-MM-DD` format. The "From" date is automatically limited to before the "To" date and vice versa.

### Applying Filters

1. Set your filter criteria
2. Click **Filter** to apply
3. The table updates with matching measurements
4. Click **Reset** to clear all filters

## Exporting as CSV

1. Set filters (optional)
2. Click the **CSV** button
3. A file downloads automatically

### CSV Format

```csv
ID,Device,Session,Bus Voltage,Shunt Voltage,Load Voltage,Current (A),Power (W),Energy (Wh),Timestamp
1,esp32-ina219-01,FW v1.0 Idle,5.120,0.082,5.038,0.241,1.234,0.000343,2026-07-18T10:00:00+00:00
2,esp32-ina219-01,FW v1.0 Idle,5.118,0.081,5.037,0.239,1.223,0.000686,2026-07-18T10:00:01+00:00
```

### CSV Columns

| Column | Unit | Description |
|--------|------|-------------|
| `ID` | — | Measurement ID |
| `Node` | — | Node ID string |
| `Session` | — | Session name (empty if none) |
| `Bus Voltage` | V | Bus voltage from INA219 |
| `Shunt Voltage` | V | Shunt voltage from INA219 |
| `Load Voltage` | V | Load voltage (bus - shunt) |
| `Current (A)` | A | Current draw |
| `Power (W)` | W | Power consumption |
| `Energy (Wh)` | Wh | Cumulative energy |
| `Timestamp` | ISO 8601 | Measurement timestamp |

### File Naming

| Scenario | Filename |
|----------|----------|
| No session filter | `measurements.csv` |
| Session filter applied | `<session_name>_report.csv` |

Session names are sanitized: special characters removed, spaces replaced with underscores.

## Exporting as XLSX

1. Set filters (optional)
2. Click the **XLSX** button
3. An Excel file downloads automatically

### XLSX Features

| Feature | Description |
|---------|-------------|
| **Formatted headers** | Bold header row |
| **Auto-sized columns** | Columns resize to fit content |
| **Single sheet** | All data in one "Measurements" sheet |
| **No formulas** | Raw data only — add your own calculations |

### File Naming

The XLSX file is always named `measurements.xlsx`.

## Using Exported Data

### Google Sheets

1. Open Google Sheets
2. Go to **File > Import**
3. Upload the CSV or XLSX file
4. Select import location

### Microsoft Excel

1. Open Excel
2. Go to **File > Open**
3. Select the XLSX or CSV file
4. For CSV: use the Import Wizard to set delimiters

### Python / Pandas

```python
import pandas as pd

# From CSV
df = pd.read_csv('measurements.csv')

# From XLSX
df = pd.read_excel('measurements.xlsx')

# Analyze
print(df.describe())
print(df.groupby('Session')['Power (W)'].mean())
```

### R

```r
# From CSV
df <- read.csv('measurements.csv')

# From XLSX
library(readxl)
df <- read_excel('measurements.xlsx')

# Analyze
summary(df)
tapply(df$Power.W., df$Session, mean)
```

### Command Line

```bash
# View CSV
column -s, -t measurements.csv | less

# Count rows
wc -l measurements.csv

# Extract specific columns
cut -d',' -f1,4,8 measurements.csv
```

## API Reference

### Export CSV

```bash
GET /api/v1/measurements/export/csv
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `device_id` | integer | No | Filter by device ID |
| `session_id` | integer | No | Filter by session ID |
| `start_date` | string | No | Start date (ISO 8601) |
| `end_date` | string | No | End date (ISO 8601) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/measurements/export/csv?session_id=1" \
  -H 'Authorization: Bearer <jwt-token>' \
  --output measurements.csv
```

**Response:**

- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=measurements.csv`

### Export XLSX

```bash
GET /api/v1/measurements/export/xlsx
```

**Parameters:** Same as CSV export.

**Example:**

```bash
curl "http://localhost:8000/api/v1/measurements/export/xlsx?device_id=1&start_date=2026-07-01T00:00:00Z" \
  -H 'Authorization: Bearer <jwt-token>' \
  --output measurements.xlsx
```

**Response:**

- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename=measurements.xlsx`

### Rate Limits

Export endpoints are rate-limited to **10 requests per minute** per IP address.

## Large Exports

For large datasets:

1. Use **session filter** to limit the export scope
2. Use **date range** to export specific time periods
3. Consider exporting in multiple smaller files

!!! warning "Memory usage"
    Exports load all matching measurements into memory. Very large exports (>100k rows) may take a few seconds to generate.

## Tips

### Automate Exports

Use cron or Task Scheduler to export data regularly:

```bash title="Daily export"
0 0 * * * curl -s "http://localhost:8000/api/v1/measurements/export/csv?start_date=$(date -d yesterday +\%Y-\%m-\%dT00:00:00Z)" -H "Authorization: Bearer <token>" -o /backups/measurements_$(date +\%Y-\%m-\%d).csv
```

### Compare Exports

Export multiple sessions separately, then compare in a spreadsheet:

1. Export Session A as `session_a.csv`
2. Export Session B as `session_b.csv`
3. Import both into Excel or Google Sheets
4. Use pivot tables or charts to compare

### Data Integrity

- Timestamps are in **UTC** (ISO 8601 format)
- All numeric values use **full precision** (no rounding in export)
- Energy values are **cumulative** (Wh)
