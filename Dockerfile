FROM odoo:19.0

USER root

# Install python-docx for DOCX report generation
RUN pip install --break-system-packages python-docx

# Copy extra-addons directory
COPY --chown=odoo:odoo extra-addons /mnt/extra-addons

USER odoo
