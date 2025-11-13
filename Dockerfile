FROM python:3.13

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    zsh

WORKDIR /app

COPY requirements.txt /app/

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/media

COPY . /app/

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
