import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Load the data
df = pd.read_csv("cancer_updates.csv")

# Sidebar filters
st.sidebar.title("Filters")
selected_date = st.sidebar.selectbox("Select Date", sorted(df['date'].unique(), reverse=True))

# Filter by date
filtered_df = df[df['date'] == selected_date]

# Title
st.title("🧪 Cancer Therapy Research Dashboard")

# Show number of articles
st.subheader(f"Articles for {selected_date}: {len(filtered_df)} articles")

# Word Cloud of titles + summaries
text = " ".join(filtered_df['title']) + " " + " ".join(filtered_df['summary'])

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

st.subheader("🧠 Most Common Keywords")
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig)

# List article titles
st.subheader("📰 Today's Articles")
for idx, row in filtered_df.iterrows():
    st.markdown(f"**{row['title']}**  \n[Read More]({row['link']})")

# Footer
st.markdown("---")
st.markdown("Dashboard powered by your Cancer Therapy Bot 🚀")
