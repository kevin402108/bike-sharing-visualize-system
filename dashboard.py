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

# 创建两行的图表布局
fig, axes = plt.subplots(2, 5, figsize=(20, 10))

# 设置第一行（星期一到星期五）
weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五']
for i, weekday in enumerate(weekdays):
    # 筛选对应星期的数据
    weekday_data = main2_df[main2_df['weekday'] == weekday]
    
    # 绘制工作日和非工作日的租赁模式
    sns.lineplot(data=weekday_data, x="hour", y="total", ax=axes[0, i], hue="workingday")
    
    # 设置标题和标签
    axes[0, i].set_title(f'{weekday}', fontsize=14)
    axes[0, i].set_xlabel('小时')
    axes[0, i].set_ylabel('租赁总数')
    axes[0, i].grid(False)
    axes[0, i].set_xlim(0, 23)  # 确保x轴范围是0-23小时
    
    # 自定义图例
    handles, labels = axes[0, i].get_legend_handles_labels()
    axes[0, i].legend(handles=handles, labels=['非工作日', '工作日'], loc='upper right')

# 设置第二行（星期六和星期日）
weekends = ['星期六', '星期日']
for i, weekend in enumerate(weekends):
    # 筛选对应周末的数据
    weekend_data = main2_df[main2_df['weekday'] == weekend]
    
    # 绘制工作日和非工作日的租赁模式
    sns.lineplot(data=weekend_data, x="hour", y="total", ax=axes[1, i], hue="workingday")
    
    # 设置标题和标签
    axes[1, i].set_title(f'{weekend}', fontsize=14)
    axes[1, i].set_xlabel('小时')
    axes[1, i].set_ylabel('租赁总数')
    axes[1, i].grid(False)
    axes[1, i].set_xlim(0, 23)  # 确保x轴范围是0-23小时
    
    # 自定义图例
    handles, labels = axes[1, i].get_legend_handles_labels()
    axes[1, i].legend(handles=handles, labels=['非工作日', '工作日'], loc='upper right')

# 隐藏多余的子图
for i in range(2, 5):
    axes[1, i].set_visible(False)

plt.tight_layout()
st.pyplot(fig)