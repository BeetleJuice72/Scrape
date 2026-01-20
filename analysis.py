import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("github_repos_1000.csv")

# -----------------------------
# ГИПОТЕЗА:
# Распределение stars является правосторонне асимметричным
# -----------------------------

plt.figure(figsize=(10, 5))
sns.histplot(
    df["stars"],
    bins=50,
    kde=True
)

plt.title("Распределение числа звёзд у GitHub-репозиториев")
plt.xlabel("Stars")
plt.ylabel("Количество репозиториев")
plt.tight_layout()
plt.show()

# Лог-шкала для наглядности
plt.figure(figsize=(10, 5))
sns.histplot(
    df["stars"],
    bins=50,
    kde=True,
    log_scale=(True, False)
)

plt.title("Распределение числа звёзд (лог-шкала)")
plt.xlabel("Stars (log)")
plt.ylabel("Количество репозиториев")
plt.tight_layout()
plt.show()

print("Описательная статистика:")
print(df["stars"].describe())
