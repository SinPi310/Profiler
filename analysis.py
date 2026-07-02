import os

import matplotlib.pyplot as plt
import pandas as pd


def analyze_ratings(file_path: str) -> None:
    df = pd.read_csv(file_path)

    if df.empty:
        print("No data found.")
        return

    df["duration_s"] = df["duration_ms"].apply(format_ms)

    average_grade = df["rate"].mean()
    album_name = os.path.splitext(os.path.basename(file_path))[0]

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(14, 9))
    fig.suptitle(f"{album_name.upper()} ({average_grade:.2f}/10)", fontsize=18, fontweight="bold")

    skrocone_tytuly = [tytul[:20] + "..." if len(tytul) > 20 else tytul for tytul in df["title"]]
    superstar_colour_all = ["gold" if str(star) == "True" else "mediumpurple" for star in df["superstar"]]

    ax[0, 0].set_title("All tracks")
    ax[0, 0].bar(skrocone_tytuly, df["rate"], color=superstar_colour_all, edgecolor="black")
    ax[0, 0].set_ylabel("Rate")
    ax[0, 0].set_ylim(0, 11)
    ax[0, 0].tick_params(axis="x", rotation=90, labelsize=9)

    top5 = df.sort_values(by="rate", ascending=False).head(5).sort_values(by="rate", ascending=True)
    superstar_colour_top5 = ["gold" if str(star) == "True" else "mediumpurple" for star in top5["superstar"]]

    ax[0, 1].barh(y=top5["title"], width=top5["rate"], color=superstar_colour_top5, edgecolor="black")
    ax[0, 1].set_title("Top 5")
    ax[0, 1].set_xlim(0, 11)

    for i, (ocena, star) in enumerate(zip(top5["rate"], top5["superstar"])):
        special = "*" if str(star) == "True" else ""
        ax[0, 1].text(ocena + 0.2, i, f"{ocena}{special}", va="center", fontweight="bold")

    ax[1, 0].axis("off")

    table_data = []
    for _, row in df.iterrows():
        table_data.append([row["title"], str(row["artist"]), format_ms(row["duration_ms"])])

    szerokosci_kolumn = [0.45, 0.40, 0.15]
    tabela = ax[1, 0].table(cellText=table_data, colWidths=szerokosci_kolumn, loc="center", cellLoc="left")

    tabela.auto_set_font_size(False)
    font_size = 9 if len(df) <= 15 else 7
    tabela.set_fontsize(font_size)
    tabela.scale(1, 1.4)

    superstar_counts = df["superstar"].astype(str).value_counts()
    superstar_colour_pie = ["gold" if val == "True" else "mediumpurple" for val in superstar_counts.index]
    etykiety = ["Superstars" if val == "True" else "Casual" for val in superstar_counts.index]

    ax[1, 1].pie(
        superstar_counts.values,
        labels=etykiety,
        autopct="%1.1f%%",
        startangle=90,
        colors=superstar_colour_pie,
        radius=1.2,
        textprops={"fontsize": 11},
    )
    ax[1, 1].set_title("Amount of superstar tracks in the album")

    plt.tight_layout()
    plt.show()


def format_ms(ms: int) -> str:
    minutes = int((ms / (1000 * 60)) % 60)
    seconds = int((ms / 1000) % 60)
    return f"{minutes:02d}:{seconds:02d}"
