#!/usr/bin/env python3
"""Convert the Firebase sales.json export into a CSV report.

Runs as part of the daily "Sync Firebase Sales Data" GitHub Action, right after
sales.json is fetched, so sales-report.csv always reflects the latest data with
no manual export step. Column layout intentionally matches the app's own
in-browser "Export CSV" button (see exportCSV() in index.html) so a report
pulled from either place looks the same, plus an Outlet column now that
records are tagged for future multi-outlet support.
"""
import csv
import json
import sys

COLUMNS = [
    'Date', 'Staff', 'Outlet', 'Retail POS', 'Retail POS Cash', 'Retail POS Card',
    'Retail Cash', 'Retail Card', 'F&B POS', 'F&B POS Cash', 'F&B POS Card',
    'F&B Cash', 'F&B Card', 'Deliveroo', 'Careem', 'Keeta', 'Tips Cash', 'Tips Card',
    'Total Cash', 'Total Card', 'Delivery', 'Tips', 'Grand Total',
    'R.Cash Var', 'R.Card Var', 'F&B Cash Var', 'F&B Card Var', 'Notes',
]


def row_for(e):
    def num(key):
        return e.get(key) or 0

    def var(key):
        v = e.get(key)
        return v if v is not None else ''

    return [
        e.get('date', ''), e.get('staff', ''), e.get('outlet') or 'Ventum Racing',
        num('retailPos'), num('retailPosCash'), num('retailPosCard'),
        num('retailCash'), num('retailCard'),
        num('fnbPos'), num('fnbPosCash'), num('fnbPosCard'),
        num('fnbCash'), num('fnbCard'),
        num('deliveroo'), num('careem'), num('keeta'),
        num('tipsCash'), num('tipsCard'),
        num('totalCash'), num('totalCard'), num('totalDelivery'), num('totalTips'), num('grand'),
        var('retailCashVar'), var('retailCardVar'), var('fnbCashVar'), var('fnbCardVar'),
        e.get('notes', ''),
    ]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'sales.json'
    dest = sys.argv[2] if len(sys.argv) > 2 else 'sales-report.csv'

    with open(src, 'r', encoding='utf-8') as f:
        raw = f.read().strip()

    data = json.loads(raw) if raw and raw != 'null' else {}
    entries = [e for e in data.values() if isinstance(e, dict)]
    entries.sort(key=lambda e: (e.get('date') or '', e.get('staff') or ''))

    with open(dest, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for e in entries:
            w.writerow(row_for(e))

    print(f'Wrote {len(entries)} rows to {dest}')


if __name__ == '__main__':
    main()
