import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    # Load data
    file_path = 'show_launch_hn_data.csv'
    df = pd.read_csv(file_path)

    # Convert UNIX time to datetime
    df['datetime'] = pd.to_datetime(df['time'], unit='s')

    # 1. Score Distribution
    plt.figure(figsize=(8, 4))
    plt.hist(df['score'], bins=20, edgecolor='black')
    plt.title('Score Distribution')
    plt.xlabel('Score')
    plt.ylabel('Number of Posts')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('score_distribution.png')

    # 2. Comments vs. Score
    plt.figure(figsize=(8, 4))
    plt.scatter(df['score'], df['descendants'], alpha=0.6)
    plt.title('Comments vs. Score')
    plt.xlabel('Score')
    plt.ylabel('Number of Comments')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('comments_vs_score.png')

    # 3. Posts Over Time
    posts_per_day = df.set_index('datetime').resample('D').size()
    plt.figure(figsize=(10, 4))
    posts_per_day.plot()
    plt.title('Number of Posts Per Day')
    plt.xlabel('Date')
    plt.ylabel('Posts')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('posts_over_time.png')

    # 4. Open Source vs Non-Open Source
    open_source_counts = df['open_source'].value_counts()
    plt.figure(figsize=(6, 4))
    open_source_counts.plot(kind='bar', color=['gray', 'green'])
    plt.title('Open Source vs Non-Open Source Posts')
    plt.xticks([0, 1], ['Non-Open Source', 'Open Source'], rotation=0)
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('open_source_bar.png')

    print("Charts saved to current directory.")

if __name__ == '__main__':
    main()