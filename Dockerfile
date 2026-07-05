# Build the alexia docker image based on Debian 11 (Bullseye)
FROM debian:trixie-slim

# Copy alexia sources
COPY . /alexia

# Set /alexia as startup working directory
WORKDIR /alexia

# Install required packages for alexia and prepare the system to run alexia
RUN echo "Updating repostitories..." && \
    apt-get update -y && \
    echo "Upgrading base debian system..." && \
    apt-get upgrade -y && \
    echo "Installing alexia required packages..." && \
    apt-get install -y apt-utils git net-tools curl python3 mariadb-client libmariadb-dev xmlsec1 libssl-dev libldap-dev libsasl2-dev libjpeg-dev zlib1g-dev gettext locales acl wkhtmltopdf xvfb && \
    echo "Installing uv..." && \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh && \
    echo "Enabling 'nl_NL' and 'en_US' locales..." && \
    sed -i -e 's/# nl_NL.UTF-8 UTF-8/nl_NL.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    echo "Rebuilding locales..." && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo "Creating directories for alexia..." && \
    mkdir -p /alexia /config /static /media /var/log /var/run && \
    echo "Installing python requirements..." && \
    uv sync --frozen && \
    echo "Correcting permissions on directories..." && \
    chown -R 1000:1000 /alexia /config /static /media /var/log

# Make the project's virtual environment available on PATH
ENV PATH="/alexia/.venv/bin:$PATH"

# Switch back to a local user
USER 1000:1000

# Check if Django can run
RUN python3 manage.py check

# Expose volumes
VOLUME ["/config", "/static", "/media"]

# Expose the web port
EXPOSE 8000

# Start the website
CMD ["/alexia/scripts/start_web_wsgi.sh"]
