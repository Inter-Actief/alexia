# Build the alexia docker image based on Debian 13 (Trixie)
FROM debian:trixie-slim

# Copy alexia sources
COPY . /alexia

# Set /alexia as startup working directory
WORKDIR /alexia

# Install required packages for alexia and prepare the system to run alexia
RUN echo "Updating repositories..." && \
    apt-get update -y && \
    echo "Upgrading base debian system..." && \
    apt-get upgrade -y && \
    echo "Installing alexia required packages..." && \
    apt-get install -y apt-utils git net-tools curl python3 python3-pip python3-dev build-essential pkg-config mariadb-client libmariadb-dev xmlsec1 libssl-dev libldap-dev libsasl2-dev libjpeg-dev zlib1g-dev gettext locales acl xvfb && \
    echo "Installing uv..." && \
    pip3 install --upgrade uv --break-system-packages && \
    echo "Installing wkhtmltopdf (no longer packaged in Debian repos)..." && \
    curl -LsSf -o /tmp/wkhtmltox.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
    apt-get install -y /tmp/wkhtmltox.deb && \
    rm /tmp/wkhtmltox.deb && \
    echo "Enabling 'nl_NL' and 'en_US' locales..." && \
    sed -i -e 's/# nl_NL.UTF-8 UTF-8/nl_NL.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    echo "Rebuilding locales..." && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo "Creating directories for alexia..." && \
    mkdir -p /alexia /config /static /media /var/log /var/run && \
    echo "Correcting permissions on directories..." && \
    chown -R 1000:1000 /alexia /config /static /media /var/log

# Switch back to a local user
USER 1000:1000

# Make the project's virtual environment available on PATH
ENV PATH="/alexia/.venv/bin:$PATH"

# uv needs a writable cache dir; the default (derived from $HOME) isn't writable for the non-root user below
ENV UV_CACHE_DIR="/config/uv-cache"

# Install requirements and check if Django can run
RUN echo "Installing python requirements..." && \
    uv sync --frozen && \
    echo "Check if Django can run..." && \
    python3 manage.py check

# Expose volumes
VOLUME ["/config", "/static", "/media"]

# Expose the web port
EXPOSE 8000

# Start the website
CMD ["/alexia/scripts/start_web_wsgi.sh"]
