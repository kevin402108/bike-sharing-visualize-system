import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

# 将"dteday"列的数据类型更改为datetime
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

# 重命名列
def rename_columns(dataframe, column_mapping):
    for old_col, new_col in column_mapping.items():
        dataframe.rename(columns={old_col: new_col}, inplace=True)

column_day = {'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'temp': 'temperature', 'hum': 'humidity', 'cnt': 'total'}
column_hour = {'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'hr': 'hour', 'temp': 'temperature', 'hum': 'humidity', 'cnt': 'total'}

rename_columns(day_df, column_day)
rename_columns(hour_df, column_hour)

# 修改季节类别名称
season_mapping = {1: '春季', 2: '夏季', 3: '秋季', 4: '冬季'}
day_df['season'] = day_df['season'].replace(season_mapping)
hour_df['season'] = hour_df['season'].replace(season_mapping)

# 修改月份类别名称
month_names = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
day_df['month'] = day_df['month'].apply(lambda x: month_names[x-1])
hour_df['month'] = hour_df['month'].apply(lambda x: month_names[x-1])

# 修改年份类别名称
year_mapping = {0: '2011年', 1: '2012年'}
day_df['year'] = day_df['year'].replace(year_mapping)
hour_df['year'] = hour_df['year'].replace(year_mapping)

# 修改星期类别名称
weekday_mapping = {0: '星期日', 1: '星期一', 2: '星期二', 3: '星期三', 4: '星期四', 5: '星期五', 6: '星期六'}
day_df['weekday'] = day_df['weekday'].replace(weekday_mapping)
hour_df['weekday'] = hour_df['weekday'].replace(weekday_mapping)

# 过滤数据
min_date = day_df["date"].min()
max_date = day_df["date"].max()

with st.sidebar:
    # 时间选择器
    start_date, end_date = st.date_input(
        label='时间范围', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main1_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]
main2_df = hour_df[(hour_df["date"] >= str(start_date)) & 
                (hour_df["date"] <= str(end_date))]

st.header('自行车租赁')

# 数据概览
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = main1_df.casual.sum()
    st.metric("非注册用户", value="{:,}".format(total_casual))

with col2:
    total_registered = main1_df.registered.sum()
    st.metric("注册用户", value="{:,}".format(total_registered))

with col3:
    total_total = main1_df.total.sum()
    st.metric("总数", value="{:,}".format(total_total))

# 可视化季节使用情况
st.subheader('季节使用情况')

plot_season = main1_df.groupby('season')[['registered', 'casual']].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 6)) 

bar_width = 0.35
bar_positions1 = range(len(plot_season['season']))
bar_positions2 = [pos + bar_width for pos in bar_positions1]

ax.bar(bar_positions1, plot_season['registered'], width=bar_width, label='注册用户', color='tab:blue')
ax.bar(bar_positions2, plot_season['casual'], width=bar_width, label='非注册用户', color='tab:orange')

ax.set_xlabel('季节')
ax.set_ylabel('租赁总数')
ax.set_title('自行车租赁数量按季节分布', fontsize=17)
ax.set_xticks([pos + bar_width/2 for pos in bar_positions1])
ax.set_xticklabels(plot_season['season'])
ax.legend()

st.pyplot(fig)

# 可视化月度使用情况
month_order = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
main1_df['month'] = pd.Categorical(main1_df['month'], categories=month_order, ordered=True)

st.subheader('月度使用情况')
fig, ax = plt.subplots(figsize=(10, 6)) 

plot_monthly = main1_df.groupby(by=["month", "year"], observed=False).agg({
    "total": "sum"
}).reset_index()

sns.lineplot(
    data=plot_monthly,
    x="month",
    y="total",
    hue="year",
    style="year",  
    markers=True,
    markersize=8,  
    dashes=False,  
    ax=ax
)

# 可视化：自行车租赁数量按月份和年份的分布
ax.grid(False)
ax.set_title("自行车租赁数量按月份和年份分布", fontsize=17)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.legend(title="年份", loc="upper right")
plt.tight_layout()

st.pyplot(fig)

#### 可视化：工作日每天的自行车使用量
st.subheader('每日使用情况')

fig, ax = plt.subplots(figsize=(10, 6)) 

plot_ym = main1_df.groupby(by=["date"], observed=False).agg({
    "total": "sum"
}).reset_index()

sns.lineplot(
    data=plot_ym,
    x="date",
    y="total",  
    markers=True,
    markersize=8,  
    dashes=False,  
    ax=ax
)
ax.set_xticks(ax.get_xticks()[::2])                                                                                                                                                             
ax.grid(False)
ax.set_title("自行车租赁数量按日期分布", fontsize=17)
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()

st.pyplot(fig)

#### 可视化：工作日使用模式
st.subheader('工作日使用模式')

mask1 = ((main2_df['workingday'] == 0) | (main2_df['holiday'] == 1))
df1 = main2_df[mask1]
mask2 = ((main2_df['workingday'] == 1) & (main2_df['holiday'] == 0))
df2 = main2_df[mask2]

plot_weekday = sns.FacetGrid(hour_df, col='weekday', hue='workingday', col_wrap=2, height=5, sharex=False)
plot_weekday.map(sns.lineplot, "hour", "total")
plot_weekday.fig.suptitle('自行车租赁模式按工作日分布', y=1.02, fontsize=20)
plot_weekday.set_axis_labels('小时', '租赁总数')
plot_weekday.add_legend()

for ax in plot_weekday.axes.flat:
    ax.set(xlabel="小时")
plot_weekday.set_titles(size=10)

plt.subplots_adjust(wspace=0.3, hspace=0.3)

st.pyplot(plot_weekday)
