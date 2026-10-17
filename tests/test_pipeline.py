import pandas as pd
from run_pipeline import main
from src.config import OUTPUT_DIR


def test_full_pipeline_outputs_add_up():
    main()

    clean = pd.read_csv(OUTPUT_DIR / 'clean_orders.csv')
    analysis = pd.read_csv(OUTPUT_DIR / 'analysis_results.csv')

    assert clean['order_id'].is_unique
    assert (clean['quantity'] > 0).all()
    assert (clean['price'] > 0).all()
    assert (clean['revenue'] - clean['quantity'] * clean['price']).abs().max() < 0.01

    country_total = analysis.loc[analysis['question'] == 'revenue_by_country', 'value'].sum()
    assert abs(country_total - clean['revenue'].sum()) < 0.01