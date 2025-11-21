FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Оновлюємо pip
RUN pip install --upgrade pip

# Копіюємо requirements.txt у тимчасову папку в образі
# (Docker бачить цей файл, бо ми змінили context на ..)
COPY requirements.txt /tmp/pip-tmp/

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# (Опціонально) Якщо хочете, щоб спочатку робочою папкою була /workspaces/okane
WORKDIR /workspaces/okane