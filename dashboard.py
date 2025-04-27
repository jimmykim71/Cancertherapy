import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# Page settings
st.set_page_config(page_title="Cancer Therapy Dashboard", layout="wide")

# Title
st.title("🧪 Cancer Therapy Research Dashboard")

# --- Weekly Trend Graph: Number of Articles per Day ---
if os.path.exists("cancer_updates.csv"):
    try:
        df = pd.read_csv("cancer_updates.csv")

        if not df.empty:
            st.subheader("📈 Weekly Trend: Number of Articles per Day")
            articles_per_day = df.groupby('date').size().reset_index(name='article_count')

            fig, ax = plt.subplots(figsize=(10,5))
            ax.plot(articles_per_day['date'], articles_per_day['article_count'], marker='o', linestyle='-')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Articles')
            ax.set_title('Cancer Therapy Articles Over Time')
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Sidebar date filter
            selected_date = st.sidebar.selectbox("Select Date", sorted(df['date'].unique(), reverse=True))
            filtered_df = df[df['date'] == selected_date]

            st.subheader(f"📅 Articles for {selected_date}: {len(filtered_df)} articles")

            # Word Cloud
            text = " ".join(filtered_df['title']) + " " + " ".join(filtered_df['summary'])
            if text.strip():
                st.subheader("🧠 Most Common Keywords")
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                ax2.imshow(wordcloud, interpolation='bilinear')
                ax2.axis("off")
                st.pyplot(fig2)
            else:
                st.info("No sufficient text to generate a word cloud.")

            # List Today's Articles
            st.subheader("📰 Today's Articles")
            for idx, row in filtered_df.iterrows():
                st.markdown(f"**{row['title']}**  \n[🔗 Read More]({row['link']})")

        else:
            st.warning("⚠️ CSV file exists but is empty. No articles yet.")
    except Exception as e:
        st.error(f"❌ Error reading or analyzing the CSV: {e}")
else:
    st.warning("⚠️ No cancer_updates.csv file found. Please run your daily bot to generate data.")
