# syntax=docker/dockerfile:1

FROM python:3.11.4

WORKDIR /Cricket-Predictive-Analysis-main

COPY requirements.txt .
RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


# Copy the current directory contents into the container at /usr/src/app
COPY . .

EXPOSE 3306

# Run app.py when the container launches
CMD ["python", "app.py"]
