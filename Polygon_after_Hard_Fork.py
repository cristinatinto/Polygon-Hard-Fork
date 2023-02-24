#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")
st.set_page_config(page_title="Polygon after Hard Fork", layout="wide",initial_sidebar_state="collapsed")



# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[5]:


st.title('Polygon activity after Hard Fork')
st.write('')
st.markdown('ETH-scaling project Polygon completed a hard fork last month in hopes of reducing gas tx_fees, as well as disruptive chain reorganizations known as reorgs, according to Coindesk. Let’s dive into the network’s health and performance leading up to and since the hard fork.')
st.markdown(' The idea of this work is to try to respond if this Hard Fork has impacted the Polygon ecosystem, if users are creating new wallets or buying tokens with their newfound fork wealth.')
st.write('This dashboard comprehens the following sections:')
st.markdown('1. Polygon main activity comparison before and after the Hard Fork')
st.markdown('2. Polygon supply before and after the Hard Fork')
st.markdown('3. Polygon development before and after the Hard Fork')
st.write('')
st.subheader('1. Polygon main activity')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the activity of Polygon ecosystem during this past month. More specifically, we will analyze the following data:')
st.markdown('● Total number transactions')
st.markdown('● Total active users')
st.markdown('● Total volume moved')
st.write('')

sql="""
with txns as(
select
  date_trunc('week',block_timestamp) as date,
  count(distinct tx_hash) as n_txns,
  count(distinct from_address) as n_wallets,
  sum(tx_fee) as tx_fee_luna
from polygon.core.fact_transactions
  where block_timestamp >= current_date - INTERVAL '10 WEEKS'
group by date
order by date desc
),
new_wallets as (
select
  date,
  count(from_address) as n_new_wallets
  from (
select
  date_trunc('week',min(block_timestamp)) as date,
  from_address
from polygon.core.fact_transactions
group by from_address
)
  where date >= current_date - INTERVAL '10 WEEKS'
group by date
)

select
  t.*,
    case when t.date>='2023-01-17' then 'After Hard Fork' else 'Before Hard Fork' end as period,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""

sql2="""
select
  trunc(block_timestamp,'week') as date,
  case when date>='2023-01-17' then 'After Hard Fork' else 'Before Hard Fork' end as period,
  sum(tx_fee) as fees,
  sum(fees) over (order by date) as cum_fees,
  avg(tx_fee) as avg_tx_fee,
  sum(gas_used) as gas,
  sum(gas) over (order by date) as cum_gas,
  avg(gas_used) as avg_gas,
  avg(gas_limit) as gas_limit,
  avg(gas_price) as gas_price
  from  polygon.core.fact_transactions
  where block_timestamp > getdate() - interval '10 WEEKS'
  group by 1,2
"""

st.experimental_memo(ttl=500000)
@st.cache
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()



with st.expander("Check the analysis"):

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily transactions evolution'))

    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Transactions comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active wallets evolution'))

    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active wallets comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='tx_fee_luna:Q',color='period')
        .properties(title='Daily tx_fees evolution',))

    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='tx_fee_luna:Q',color='period')
        .properties(title='tx_fees comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='gas:Q',color='period')
        .properties(title='Daily gas evolution',))

    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='avg_gas:Q',color='period')
        .properties(title='Gas comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='gas_limit:Q',color='period')
        .properties(title='Daily gas limit evolution',))

    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='gas_limit:Q',color='period')
        .properties(title='Gas limit comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='gas_price:Q',color='period')
        .properties(title='Daily gas price evolution',))

    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='gas_price:Q',color='period')
        .properties(title='Gas price comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new users evolution'))

    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New users comparison'))




# In[7]:


st.subheader("2. Supply before and after Hard Fork")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the MATIC supply. More specifically, we will analyze the following data:')
st.markdown('● $MATIC supply')
st.markdown('● Circulating supply')



sql="""
with SEND as
(select MATIC_FROM_ADDRESS,
  sum(AMOUNT) as sent_amount
from
polygon.core.ez_matic_transfers where amount is not null
group by MATIC_FROM_ADDRESS
  ),

RECEIVE as
(select MATIC_TO_ADDRESS,
  sum(AMOUNT) as received_amount
from
polygon.core.ez_matic_transfers where amount is not null
group by MATIC_TO_ADDRESS
  ),
total_supp as (select sum(received_amount) as total_supply
  from RECEIVE r
  left join SEND s on r.MATIC_TO_ADDRESS=s.MATIC_FROM_ADDRESS
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when SYMBOL_IN like '%WMATIC%' then AMOUNT_IN/pow(10,18) else null end) as from_amountt,
sum(case when SYMBOL_OUT like '%WMATIC%' then AMOUNT_OUT/pow(10,18) else null end) as to_amountt,
from_amountt+to_amountt as circulating_volume
from
  polygon.sushi.ez_swaps where amount_in is not null and amount_out is not null
group by 1
),
  t3 as (select
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio
  from t3 join total_supp
where
date='2023-01-15'
    """

sql2="""
with SEND as
(select MATIC_FROM_ADDRESS,
  sum(AMOUNT) as sent_amount
from
polygon.core.ez_matic_transfers where amount is not null
group by MATIC_FROM_ADDRESS
  ),

RECEIVE as
(select MATIC_TO_ADDRESS,
  sum(AMOUNT) as received_amount
from
polygon.core.ez_matic_transfers where amount is not null
group by MATIC_TO_ADDRESS
  ),
total_supp as (select sum(received_amount) as total_supply
  from RECEIVE r
  left join SEND s on r.MATIC_TO_ADDRESS=s.MATIC_FROM_ADDRESS
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when SYMBOL_IN like '%WMATIC%' then AMOUNT_IN/pow(10,18) else null end) as from_amountt,
sum(case when SYMBOL_OUT like '%WMATIC%' then AMOUNT_OUT/pow(10,18) else null end) as to_amountt,
from_amountt+to_amountt as circulating_volume
from
  polygon.sushi.ez_swaps where amount_in is not null and amount_out is not null
group by 1
),
  t3 as (select
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio
  from t3 join total_supp
where
date='2023-01-24'

"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    col1,col2=st.columns(2)
    with col1:
        st.metric('Total supply before Hard Fork',df['total_supply'])
    col2.metric('Total supply after Hard Fork',df2['total_supply'])

    col1,col2=st.columns(2)

    with col1:
        st.metric('Circulating supply before Hard Fork',df['circulating_supply'])
    col2.metric('Circulating supply after Hard Fork',df2['circulating_supply'])

    col1,col2=st.columns(2)
    with col1:
        st.metric('Ratio before Hard Fork',df['ratio'])
    col2.metric('Ratio after Hard Fork',df2['ratio'])




# In[8]:


st.subheader("3. Ecosystem development before and after Hard Fork")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Polygon main ecosystem development. More specifically, we will analyze the following data:')
st.markdown('● New deployed contracts')
st.markdown('● Used contracts')
st.markdown('● Swaps activity')



sql="""
select
   date_trunc('week',block_timestamp) as date,
   case when date>='2023-01-17' then 'After Hard Fork' else 'Before Hard Fork' end as period,
  count(distinct contract_address) as n_contracts,
  sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
from polygon.core.fact_event_logs
where block_timestamp>=current_date-INTERVAL '10 WEEKS'
group by date, period
order by date desc


"""


sql2="""
with new_contracts as (
select
distinct contract_address,
min(trunc(block_timestamp,'week')) as debut
from polygon.core.fact_event_logs group by 1
)
select
   debut as date,
   case when debut>='2023-01-17' then 'After Hard Fork' else 'Before Hard Fork' end as period,
  count(distinct contract_address) as n_contracts,
  sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
from new_contracts
where debut>=current_date-INTERVAL '10 WEEKS'
group by date, period
order by date desc
"""


sql3="""
with txns as(
select
  date_trunc('week',block_timestamp) as date,
      case when date>='2023-01-17' then 'After Hard Fork' else 'Before Hard Fork' end as period,
  count(distinct tx_hash) as n_txns,
  count(distinct origin_from_address) as n_wallets,
  sum(n_txns) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_txns,
  sum(n_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_wallets
from polygon.core.fact_event_logs
  where block_timestamp >= current_date - INTERVAL '10 WEEKS'
  and (event_name='Swap' or event_name='swap')
group by date, period
order by date desc
),
new_wallets as (
select
  date,
  count(origin_from_address) as n_new_wallets
  from (
select
  date_trunc('week',min(block_timestamp)) as date,
  origin_from_address
from polygon.core.fact_event_logs where (event_name='Swap' or event_name='swap')
group by origin_from_address
)
   where date >= current_date - INTERVAL '10 WEEKS'
group by date
)

select
  t.*,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""




results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()



with st.expander("Check the analysis"):

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily new contracts evolution'))

    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='New contracts comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily active contracts evolution'))

    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='Active contracts comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily swaps evolution'))

    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Swaps comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active swappers evolution'))

    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active swappers comparison'))

    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new swappers evolution'))

    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New swappers comparison'))

st.markdown('')
st.subheader('Key insights')
st.markdown('- The recent hard-fork effort by Polygon has failed to effectively reduce gas fees for transactions, resulting in an uptick of gas fees collected. Despite consistent user count and transaction volume pre- and post-fork, the increase in gas fees cannot be attributed to user behavior.')
st.markdown('- Several platforms have contributed to the recent surge in gas fees, along with other protocols operating on the Polygon network. However, despite this, Polygon remains competitive with other Layer 2 networks in terms of gas fees.')
st.markdown('- While the Optimism network boasts impressively low gas fees, when factoring in the projects and activity present on the Polygon network, the cons seen in gas fees are somewhat evened out. Nonetheless, reducing gas fees remains a top priority for the Polygon team in order to enhance the networks efficiency and competitiveness. The challenge is on, and we cant wait to see how the Polygon team will tackle it!)    
st.markdown('')
st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')
st.markdown('All codes can be found here: https://github.com/cristinatinto/Polygon-Hard-Fork')


# In[ ]:
