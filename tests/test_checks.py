import pandas as pd
import pytest
from src.checks import run_checks, reconcile


def make_order(**changes):
    row = {
        'order_id': '1-1', 'customer_id': '100', 'product_id': 'A',
        'order_date': pd.Timestamp('2011-09-01 10:00:00'),
        'quantity': 5, 'price': 2.0,
        'customer_found': True, 'product_found': True,
    }
    row.update(changes)
    return row


def test_good_order_passes_every_check():
    results = run_checks(pd.DataFrame([make_order()]))
    assert results.all(axis=1)[0]


def test_bad_values_fail_the_right_checks():
    joined = pd.DataFrame([
        make_order(order_id='1-1', quantity=-2),
        make_order(order_id='1-2', price=0),
        make_order(order_id='1-3', order_date=pd.Timestamp('2030-01-01')),
        make_order(order_id='1-4', customer_found=False),
    ])
    results = run_checks(joined)
    assert not results['quantity_positive'][0]
    assert not results['price_positive'][1]
    assert not results['order_date_valid'][2]
    assert not results['customer_matched'][3]


def test_missing_customer_is_reported_once():
    joined = pd.DataFrame([make_order(customer_id=None, customer_found=False)])
    results = run_checks(joined)
    assert not results['customer_id_present'][0]
    assert results['customer_matched'][0]


def test_both_copies_of_a_repeated_order_id_fail():
    joined = pd.DataFrame([make_order(order_id='1-1'), make_order(order_id='1-1', quantity=9)])
    results = run_checks(joined)
    assert not results['order_id_unique'].any()


def test_reconciliation_fails_when_rows_go_missing():
    with pytest.raises(ValueError):
        reconcile(input_rows=100, clean_rows=90, failed_rows=5, duplicates_removed=3)