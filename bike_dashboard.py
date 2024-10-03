import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap

# Load CSV files
df_day = pd.read_csv('./data/day.csv')
df_hour = pd.read_csv('./data/hour.csv')

### CLEANING DATA ###
# Change the dteday format
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

# Convert holiday and workingday columns to boolean df_day
df_day['holiday'] = df_day['holiday'].astype(bool)
df_day['workingday'] = df_day['workingday'].astype(bool)

# Convert holiday and workingday columns to boolean df_hour
df_hour['holiday'] = df_hour['holiday'].astype(bool)
df_hour['workingday'] = df_hour['workingday'].astype(bool)

# Create Categorize for df_temp.
def categorize_temperature(temp):
    if temp < 16:
        return 'low'       
    elif 16 <= temp <= 30:
        return 'medium'   
    else:
        return 'high'  

# Mapping dictionaries
def map_columns(df):
    # Mapping dictionaries
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    yr_map = {0: '2011', 1: '2012'}
    mnth_map = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    weekday_map = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
        4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    }
    weather_map = {
    1: 'Clear, Few clouds, Partly cloudy',
    2: 'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
    3: 'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds',
    4: 'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog'
    }

    # Applying the mapping
    df['season'] = df['season'].replace(season_map)
    df['yr'] = df['yr'].replace(yr_map)
    df['mnth'] = df['mnth'].replace(mnth_map)
    df['weekday'] = df['weekday'].replace(weekday_map)
    df['weathersit'] = df['weathersit'].replace(weather_map)

    return df

# Applying the mapping
df_day = map_columns(df_day)
df_hour = map_columns(df_hour)
### END OF CLEANING DATA ###

# Create the main app layout
st.title("Bicycle Rental Dashboard")

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Exploratory Data Analysis", "Analisis Lanjutan"])

# First Tab: Overview
with tab1:
    st.header("Overview of the Data")
    st.write("### Bike Sharing on Daily Basis")
    st.dataframe(df_day.set_index('instant'))

    st.write("### Bike Sharing on Hour Basis")
    st.dataframe(df_hour.set_index('instant'))

    # Dataset Descriptions
    with st.expander("Column Description"):
        st.markdown("""
        - **instant**: index record
        - **dteday**: date
        - **season**: season 
        - **yr**: year 
        - **mnth**: month (1 to 12)
        - **hr**: hour (0 to 23)
        - **holiday**: weather day is holiday or not 
        - **weekday**: day of the week
        - **workingday**: working day or not
        - **weathersit**:
            - Clear, Few clouds, Partly cloudy
            - Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds
            - Light Snow, Light Rain + Thunderstorm + Scattered clouds
            - Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog
        - **temp**: Normalized temperature in Celsius (divided by 41)
        - **atemp**: Normalized feeling temperature in Celsius (divided by 50)
        - **hum**: Normalized humidity (divided by 100)
        - **windspeed**: Normalized wind speed (divided by 67)
        - **casual**: count of casual users
        - **registered**: count of registered users
        - **cnt**: count of total rental bikes (casual + registered)
        """)
    
# Second Tab: EDA Statistics (with sidebar)
with tab2:
    with st.expander('Based on Weather'):
        st.subheader('Persebaran Jumlah Total Penyewaan Sepeda Terhadap Musim')

        # Group number of rentals (cnt) by season
        df_season = df_day.groupby('season').agg({
            'cnt': ['sum','median','mean','std']
        })

        # Flattening the MultiIndex columns
        df_season.columns = ['cnt_sum', 'cnt_median', 'cnt_mean', 'cnt_std']

        # Sort the DataFrame by cnt_sum
        df_season_sorted = df_season.sort_values(by='cnt_sum', ascending=False)

        # Identify the maximum value
        max_value = df_season_sorted['cnt_sum'].max()

        # Create a color list based on cnt_sum
        colors = ['darkblue' if value == max_value else '#1f77b4' for value in df_season_sorted['cnt_sum']]

        # Create a bar plot for cnt_sum using Matplotlib and Seaborn
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_season_sorted.reset_index(), x='season', y='cnt_sum', palette=colors)

        # Add titles and labels
        plt.title('Number of Rental Counts by Season')
        plt.xlabel('Season')
        plt.ylabel('Counts')
        plt.xticks(rotation=0)
        
        # Show the plot in Streamlit
        st.pyplot(plt)
        st.write("Insight :")
        st.write("* **Musim Gugur Jadi Waktu Favorit untuk Sewa Sepeda:** Kebanyakan orang lebih suka menyewa sepeda di musim gugur (Fall), mungkin karena cuacanya yang sejuk dan nyaman untuk bersepeda")
        st.write("* **Urutan Penyewaan Berdasarkan Musim:** Setelah musim gugur, penyewaan sepeda terbanyak terjadi di musim panas (Summer), kemudian musim dingin (Winter), dan terakhir di musim semi (Spring)")
        
    with st.expander("Based on Daily Basis"):
        st.subheader("Persebaran Penyeberan Rental Sepeda Per hari")
        # Group number of rentals (cnt) by hour
        df_hour_cnt = df_hour.groupby('hr').agg({
            'cnt': ['min', 'max', 'median', 'mean', 'std']
        })

        # Reset the index to flatten the DataFrame
        df_hour_cnt.columns = ['cnt_min', 'cnt_max', 'cnt_median', 'cnt_mean', 'cnt_std']

        # Create a line plot for cnt_mean
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_hour_cnt, x=df_hour_cnt.index, y='cnt_mean', marker='o')

        # Add titles and labels
        plt.title('Average Bicycle Rentals by Hour')
        plt.xlabel('Hour of the Day')
        plt.ylabel('Average Number of Rentals')
        plt.xticks(range(0, 24))  # Show all hours on x-axis

        # Show the plot in Streamlit
        plt.tight_layout()
        st.pyplot(plt) 
        st.write("Insight :")
        st.write("* **Peningkatan Penggunaan pada Pagi Hari:** Rata-rata penggunaan sepeda mengalami peningkatan yang signifikan pada pukul 8 pagi. Waktu ini menandakan adanya lonjakan aktivitas bersepeda yang mungkin berkaitan dengan jam sibuk saat orang-orang berangkat bekerja atau sekolah")
        st.write("* **Penggunaan Sepeda Meningkat pada Sore Hari:** Penggunaan sepeda kembali meningkat antara jam 4 sore hingga 7 malam. Rentang waktu ini menunjukkan aktivitas bersepeda yang tinggi setelah jam kerja atau kegiatan lainnya, di mana banyak orang memanfaatkan sepeda untuk pulang")
        st.write("* **Puncak Penggunaan pada Jam 5 hingga 6 Sore:** Puncak penggunaan sepeda terjadi antara jam 5 hingga 6 sore, dengan rata-rata lebih dari 400 pengguna pada saat tersebut. Ini merupakan waktu tersibuk dalam sehari, yang mencerminkan tingginya permintaan terhadap sepeda selama periode ini")
           
    
    with st.expander("Based on Workingday and Holiday"):
        st.subheader("Pengaruh Weekend/Holiday terhadap Perilaku Penyewaan Sepeda")
        # Group number of rentals (cnt) by working day
        df_holiday = df_day.groupby(['workingday']).agg({
            'cnt': ['median', 'mean', 'std']
        })

        df_holiday.reset_index(inplace=True)  # Resetting index to keep 'workingday' as a column
        df_holiday.columns = ['workingday', 'cnt-mean', 'cnt-median', 'cnt-std']  # Rename columns

        mean_values = df_holiday['cnt-mean']
        labels = df_holiday['workingday'].map({False: 'Holiday', True: 'Working Day'})

        # Explosion for the pie chart
        explode = (0.02, 0.02)

        # Create Plot
        plt.figure(figsize=(8, 6))
        plt.pie(mean_values, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.7, explode=explode)

        # Create Circle for the donut plot
        centre_circle = plt.Circle((0, 0), 0.5, fc='white')  # Circle Radius 
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.title('Distribution of Average Bicycle Rentals for Holiday')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        # Show the plot in Streamlit
        st.pyplot(plt)
        st.write("Insight:")
        st.write("* Meskipun terdapat perbedaan aktivitas antara hari libur dan hari kerja, jumlah penyewaan sepeda cenderung tetap stabil dan tidak menunjukkan variasi signifikan. Baik pada hari kerja maupun hari libur, permintaan untuk penyewaan sepeda relatif sama")

    with st.expander("Based on Weather Situation"):
        st.subheader("Penyebaran Jumlah Penyewaan Sepeda Terhadap Kondisi Cuaca")
        # Group number of rentals (cnt) by weather situation
        df_weathersit = df_hour.groupby(['weathersit']).agg({
            'cnt': ['sum', 'median', 'mean', 'std']
        })

        # Sort by cnt sum
        df_weathersit.sort_values(by=('cnt', 'sum'), ascending=False, inplace=True)

        sum_values = df_weathersit[('cnt', 'sum')]
        labels = df_weathersit.index  # Index will be the weather situation

        # Shorten the labels by wrapping the text
        wrapped_labels = [textwrap.fill(label, 20) for label in labels]

        # Create a figure size
        plt.figure(figsize=(15, 6))

        # Create a bar plot with Seaborn
        colors = ['#1f77b4' if value < sum_values.max() else 'darkblue' for value in sum_values]
        ax = sns.barplot(y=wrapped_labels, x=sum_values, palette=colors, orient='h')

        # Add the count value to each bar
        for index, value in enumerate(sum_values):
            ax.text(value, index, f'{int(value)}', va='center')

        plt.title('Rentals by Weather Situation')
        plt.xlabel('Total Count (cnt-sum)')
        plt.ylabel('Weather Situation')
        plt.tight_layout()  # Adjust layout

        # Show the plot in Streamlit
        st.pyplot(plt)  
        st.write("Insight:")
        st.write("* **Cuaca Cerah dan Berawan Paling Mendukung Penyewaan:** Cuaca cerah dan berawan menjadi kondisi yang paling banyak menarik orang untuk menyewa sepeda, menunjukkan bahwa pengguna lebih suka bersepeda dalam kondisi cuaca yang nyaman")
        st.write("* **Cuaca Berkabut Sedikit Mengurangi Penyewaan:** Cuaca berkabut masih cukup mendukung aktivitas penyewaan sepeda, meskipun jumlahnya tidak setinggi pada cuaca cerah atau berawan")
        st.write("* **Hujan dan Salju Mengurangi Penyewaan Secara Signifikan:** Penyewaan sepeda menurun tajam saat hujan ringan, salju ringan, dan kondisi yang lebih ekstrem seperti hujan deras atau salju lebat, karena kondisi ini kurang mendukung untuk aktivitas bersepeda")

# Third Tab: EDA Visualizations (with sidebar)
with tab3:
    st.subheader("Correlation between Weather Parameter")
    
    # Prepare the data for correlation
    df_weather = df_hour[['temp', 'atemp', 'hum', 'windspeed', 'cnt']]
    correlation_weather = df_weather.corr()

    # Set figure size for the heatmap
    plt.figure(figsize=(8, 6))

    # Create heatmap
    sns.heatmap(correlation_weather, annot=True, cmap='coolwarm', fmt=".2f", square=True, cbar_kws={"shrink": .8})

    # Show the plot in Streamlit
    st.pyplot(plt) 
    st.write("Dari gambar di bawah dapat dilihat, terdapat korelasi positif antara suhu aktual (temp) dan suhu prediksi (atemp) dengan jumlah penyewaan sepeda (cnt), di mana artinya semakin tinggi suhu, semakin banyak penyewaan sepeda yang terjadi.")

    df_temp = df_hour[['temp','cnt']]
    df_temp['temp'] = df_temp['temp'] * 41
    
    df_temp['temp_category'] = df_temp['temp'].apply(categorize_temperature)
    category_order = ['low', 'medium', 'high']
    df_temp['temp_category'] = pd.Categorical(df_temp['temp_category'], categories=category_order, ordered=True)

    # Group by temperature category and aggregate
    df_temp_data = df_temp.groupby('temp_category').agg({
        'cnt': ['sum', 'median', 'mean', 'std']
    })

    # Get the mean value
    mean_values = df_temp_data['cnt']['mean']

    # Identify the maximum value
    max_value = mean_values.max()

    # Create a color list based on mean_values
    colors = ['darkblue' if value == max_value else '#1f77b4' for value in mean_values]

    # Create bar plot
    plt.figure(figsize=(8, 6))
    mean_values.plot(kind='bar', color=colors)  # Pass colors here

    # Add title and axis labels
    plt.xlabel('Temperature Category')
    plt.ylabel('Average Number of Rentals')
    plt.title('Average Number of Rentals by Temperature Category')

    # Show the plot in Streamlit
    plt.xticks(rotation=0)  
    
    st.subheader("Average Number of Rentals by Temperature Category")
    
    st.markdown("""Dalam proses analisis data eksploratif (EDA) ini 
                akan berfokus pada hubungan antara kategori suhu dengan jumlah penyewaan sepeda. 
                Gambar di bawah menampilkan diagram batang yang mengelompokkan data penyewaan sepeda berdasarkan tiga kategori suhu: rendah (low), sedang (medium), dan tinggi (high). 
                Kategori ini dibentuk melalui proses pengelompokan suhu ke dalam rentang-rentang tertentu untuk memudahkan analisis tren penggunaan sepeda.
                """)
    st.write("1.  **Low:** Jika suhu di bawah 16°C, dikategorikan sebagai \"low\" (suhu rendah)")
    st.write("2.  **Medium:** Jika suhu antara 16°C hingga 30°C, dikategorikan sebagai \"medium\" (sedang)")
    st.write("3.  **High:** Jika suhu di atas 30°C, dikategorikan sebagai \"high\" (tinggi)")

    st.pyplot(plt)  
    
    st.write("Sebagian besar orang cenderung lebih memilih menyewa sepeda saat suhu tinggi (di atas 30°C), diikuti oleh penyewaan pada suhu sedang (16-30°C), dan jumlah penyewaan terendah terjadi pada suhu rendah (di bawah 16°C), menunjukkan preferensi pengguna untuk bersepeda dalam kondisi yang lebih hangat.")