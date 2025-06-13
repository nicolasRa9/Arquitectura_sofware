FROM python:3.11-slim AS base
WORKDIR /app

# Copiamos el código completo
COPY . /app

# Instalación de dependencias si las hubiera (requirements.txt opcional)
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Argumento para indicar el script a ejecutar
ARG SERVICE
ENV SERVICE=${SERVICE}

# Puerto por defecto expuesto (se puede sobrescribir)
EXPOSE 9001 9002 9003 9004 9005 9100

CMD [ "sh", "-c", "python $SERVICE" ]