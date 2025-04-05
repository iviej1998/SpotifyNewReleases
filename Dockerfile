# Dockerfile to containerize the Spotify New Releases Streamlit App
FROM python:3.12
LABEL maintainer="Jillian Ivie <iviej@my.erau.edu>"

# set the timezone
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Phoenix /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# set the working directory inside the container
WORKDIR /spotifynewreleases/

# copy project files into the container
COPY . /spotifynewreleases

# install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#  environment variables to improve Python behavior in Docker
#  prevents Python from writing .pyc files to disk
#  ensures that the python output is sent straight to terminal (e.g. the container log) without being first buffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/spotifynewreleases

# expose the Streamlit default port
EXPOSE 8501

# command to run the Streamlit app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]