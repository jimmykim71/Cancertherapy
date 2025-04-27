from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import feedparser
import re
import os
import pickle
import pandas as pd
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

RSS_FEEDS = [
    'https://www.nature.com/nature/articles?type=article.rss',
    'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science',
    'https://www.thelancet.com/rssfeed/lancetoncology',
    'https://www.nejm.org/rss/topic/cancer.xml',
    'https://jamanetwork.com/rss/site_12/0.xml'
]

KEYWORDS = ['cancer', 'therapy', 'oncology']

# --- FUNCTIONS ---

def gmail_login():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_articles_from_feeds():
    all_articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_articles.append({
                'title': entry.title,
                'summary': entry.get('summary', ''),
                'link': entry.link
            })
    return all_articles

def clean_summary(text):
    clean = re.sub(r'<.*?>', '', text)
    return clean.strip()

def filter_articles(articles, keywords):
    filtered = []
    for article in articles:
        text = f"{article['title']} {article['summary']}"
        if any(keyword.lower() in text.lower() for keyword in keywords):
            filtered.append(article)
    return filtered

def summarize_text(text, sentence_count=2):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, sentence_count)
        return ' '.join(str(sentence) for sentence in summary)
    except Exception as e:
        print("Summarization Error:", e)
        return text

def create_email_body(articles):
    if not articles:
        return "<p>No cancer therapy updates found today.</p>"

    email_content = "<h2>🧪 Latest Cancer Therapy Research Updates</h2><br>"
    for idx, article in enumerate(articles, 1):
        cleaned_summary = clean_summary(article['summary'])
        short_summary = summarize_text(cleaned_summary)

        email_content += f"""
        <div style="margin-bottom:20px; padding:10px; border-bottom:1px solid #ccc;">
            <h3 style="margin-bottom:5px;">{idx}. {article['title']}</h3>
            <p><b>Summary:</b> {short_summary}</p>
            <p><a href="{article['link']}" target="_blank" style="color:blue;">🔗 Read Full Article</a></p>
        </div>
        """
    email_content += "<br><p style='font-size:small; color:gray;'>This daily email was generated automatically by your Cancer Therapy Bot.</p>"
    return email_content

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text, "html")  # send as HTML
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}

def send_message(service, user_id, message):
    sent_message = service.users().messages().send(userId=user_id, body=message).execute()
    print(f"Message Id: {sent_message['id']}")
    return sent_message

def save_articles_to_csv(articles, filename="cancer_updates.csv"):
    today = datetime.today().strftime('%Y-%m-%d')
    data = []
    for article in articles:
        cleaned_summary = clean_summary(article['summary'])
        data.append({
            "date": today,
            "title": article['title'],
            "summary": cleaned_summary,
            "link": article['link']
        })
    df = pd.DataFrame(data)
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', index=False, header=False)
    else:
        df.to_csv(filename, index=False)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    service = gmail_login()

    sender_email = "kimjames@gmail.com"  # 👈 Your email
    receiver_email = "kimjames@gmail.com"  # 👈 Your email

    all_articles = fetch_articles_from_feeds()
    cancer_articles = filter_articles(all_articles, KEYWORDS)

    # Save today's articles into cancer_updates.csv
    save_articles_to_csv(cancer_articles)

    # Prepare and send email
    email_body = create_email_body(cancer_articles)
    subject = "🧪 Cancer Therapy Research Updates Today!"
    email_message = create_message(sender_email, receiver_email, subject, email_body)
    send_message(service, 'me', email_message)
