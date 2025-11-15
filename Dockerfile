FROM odoo:19.0

USER root

# Install python-docx for DOCX report generation
RUN pip install --break-system-packages python-docx

# Install postgresql-client for database checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy nexaml addon to extra-addons directory
COPY --chown=odoo:odoo addons/nexaml /mnt/extra-addons/nexaml

# Copy custom entrypoint
COPY --chown=odoo:odoo entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--dev=all", "--log-level=debug"]
