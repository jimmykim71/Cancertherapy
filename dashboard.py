import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# Page settings
st.set_page_config(page_title="Cancer Therapy Dashboard", layout="wide")

# Title
st.title("🧪 Cancer Therapy Research Dashboard")

# -----> DO NOT READ CSV AT THE TOP <-----

# Only attempt to read if the file exists
if os.path.exists("cancer_updates.csv"):
    try:
        df = pd.read_csv("cancer_updates.csv")

        if not df.empty:
            selected_date = st.sidebar.selectbox("Select Date", sorted(df['date'].unique(), reverse=True))
            filtered_df = df[df['date'] == selected_date]

            st.subheader(f"📅 Articles for {selected_date}: {len(filtered_df)} articles")

            # Word Cloud
            text = " ".join(filtered_df['title']) + " " + " ".join(filtered_df['summary'])
            if text.strip():
                st.subheader("🧠 Most Common Keywords")
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.info("No sufficient text to generate a word cloud.")

            st.subheader("📰 Today's Articles")
            for idx, row in filtered_df.iterrows():
                st.markdown(f"**{row['title']}**  \n[🔗 Read More]({row['link']})")

        else:
            st.warning("⚠️ CSV file exists but no articles inside.")
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
else:
    st.warning("⚠️ No data available. Please run the email bot to generate cancer_updates.csv.")
