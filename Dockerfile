FROM odoo:19.0

USER root

# Install python-docx for DOCX report generation
RUN pip install --break-system-packages python-docx

# Install postgresql-client for database checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy extra-addons directory
COPY --chown=odoo:odoo extra-addons /mnt/extra-addons

# Copy custom company logo
COPY --chown=odoo:odoo logo.png /usr/lib/python3/dist-packages/odoo/addons/base/static/img/res_company_logo.png

# Copy custom entrypoint
COPY --chown=odoo:odoo entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons", "--dev=all", "--log-level=debug"]
