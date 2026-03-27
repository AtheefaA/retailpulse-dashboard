import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('retailpulse_clean.csv', parse_dates=['order_purchase_timestamp'])

# ── A: Monthly sales trend ────────────────────────────────────────────
monthly = df.groupby(['order_year', 'order_month'])['total_revenue'].sum().reset_index()
monthly['period'] = pd.to_datetime(monthly[['order_year','order_month']].assign(day=1))

plt.figure(figsize=(12,4))
plt.plot(monthly['period'], monthly['total_revenue'], marker='o', color='steelblue')
plt.title('Monthly Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Revenue (BRL)')
plt.tight_layout()
plt.savefig('monthly_revenue.png', dpi=150)

# ── B: Top 10 product categories ─────────────────────────────────────
top_cats = (df.groupby('product_category_name')['total_revenue']
              .sum()
              .sort_values(ascending=False)
              .head(10))
print("Top 10 categories:\n", top_cats)

# ── C: Customer segmentation using RFM ───────────────────────────────
snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

rfm = df.groupby('customer_unique_id').agg(
    Recency   = ('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
    Frequency = ('order_id', 'nunique'),
    Monetary  = ('total_revenue', 'sum')
).reset_index()

# Score each dimension 1-4 (4 = best)
rfm['R_score'] = pd.qcut(rfm['Recency'],   4, labels=[4,3,2,1])
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
rfm['M_score'] = pd.qcut(rfm['Monetary'],  4, labels=[1,2,3,4])
rfm['RFM_total'] = rfm[['R_score','F_score','M_score']].astype(int).sum(axis=1)

# Segment labels
def segment(score):
    if score >= 10: return 'Champions'
    elif score >= 7: return 'Loyal Customers'
    elif score >= 5: return 'At Risk'
    else: return 'Lost'

rfm['Segment'] = rfm['RFM_total'].apply(segment)
print(rfm['Segment'].value_counts())
rfm.to_csv('rfm_segments.csv', index=False)

# ── D: Region-wise performance ────────────────────────────────────────
region = (df.groupby('customer_state')
            .agg(total_revenue=('total_revenue','sum'),
                 total_orders=('order_id','nunique'),
                 avg_order_value=('total_revenue','mean'))
            .sort_values('total_revenue', ascending=False)
            .reset_index())
print("Top 5 states by revenue:\n", region.head())
region.to_csv('region_performance.csv', index=False)