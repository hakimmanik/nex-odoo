FROM odoo:19.0

USER root

# Install python-docx for DOCX report generation
RUN pip install --break-system-packages python-docx

# Copy nexaml addon to extra-addons directory
COPY --chown=odoo:odoo addons/nexaml /mnt/extra-addons/nexaml

USER odoo
