import pandas as pd
from src.clean import clean_text, clean_orders, clean_products, clean_customers


def test_clean_text_trims_and_collapses_spaces():
    result = clean_text(pd.Series(['  RED  MUG ', 'BLUE']))
    assert result.tolist() == ['RED MUG', 'BLUE']


def test_product_id_is_trimmed_and_uppercased():
    products = pd.DataFrame({'product_id': [' 85123a '], 'product_name': ['heart'],
                             'category': [' kitchen '], 'price': ['2.95']})
    result = clean_products(products)
    assert result['product_id'][0] == '85123A'
    assert result['category'][0] == 'Kitchen'
    assert result['price'][0] == 2.95


def test_invalid_date_becomes_empty_but_raw_value_is_kept():
    orders = pd.DataFrame({'order_id': ['1-1'], 'customer_id': ['100'], 'product_id': ['A'],
                           'order_date': ['2011-02-30 10:00:00'], 'quantity': ['5']})
    result = clean_orders(orders)
    assert pd.isna(result['order_date'][0])
    assert result['order_date_raw'][0] == '2011-02-30 10:00:00'


def test_country_alias_and_casing_are_standardized():
    customers = pd.DataFrame({'customer_id': ['1', '2'], 'customer_name': ['CUSTOMER 1', 'Customer 2'],
                              'email': ['A@EXAMPLE.COM', None], 'country': ['UK', ' united kingdom ']})
    result = clean_customers(customers)
    assert result['country'].tolist() == ['United Kingdom', 'United Kingdom']
    assert result['customer_name'][0] == 'Customer 1'
    assert result['email'][0] == 'a@example.com'