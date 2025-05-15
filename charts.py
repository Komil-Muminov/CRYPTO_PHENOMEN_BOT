# charts.py

import matplotlib.pyplot as plt
from io import BytesIO


def generate_portfolio_chart(portfolio_data):
    """
    Генерирует круговую диаграмму распределения портфеля.

    :param portfolio_data: dict с данными о портфеле (результат calculate_portfolio)
    :return: BytesIO изображение графика
    """
    assets = portfolio_data.get('assets', [])
    
    if not assets:
        # Если нет активов — возвращаем пустое изображение с сообщением
        plt.figure(figsize=(6, 6))
        plt.text(0.5, 0.5, 'Нет данных для отображения', ha='center', va='center', fontsize=12)
        plt.axis('off')

        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        return img

    labels = [a['symbol'] for a in assets]
    sizes = [a['current'] for a in assets]

    plt.figure(figsize=(6, 6))
    colors = plt.cm.Paired(range(len(labels)))  # Разные цвета для каждого актива

    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        shadow=True,
        textprops={'fontsize': 10}
    )
    plt.title("📊 Распределение портфеля", fontsize=14)
    plt.axis('equal')  # Круговой вид

    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    return img