# Temple Sponsor Management Application - Production Deployment Guide

This guide explains how to deploy the Temple Sponsor Management application to production on Replit and manage data access.

## Deployment on Replit

1. Fork the project:
   - Go to the original Replit project.
   - Click on the "Fork" button to create your own copy.

2. Set up environment variables:
   - In your forked Replit project, go to the "Secrets" tab (lock icon).
   - Add the following environment variables:
     - `FLASK_SECRET_KEY`: A long, random string for Flask's secret key
     - `DATABASE_URL`: The PostgreSQL database URL (provided by Replit)
     - `MAIL_USERNAME`: Your Gmail address
     - `MAIL_PASSWORD`: Your Gmail app password
     - `MAIL_DEFAULT_SENDER`: Your Gmail address

3. Install dependencies:
   - Replit automatically installs dependencies from `pyproject.toml`.
   - If any dependencies are missing, use the Replit packager to install them.

4. Set up the database:
   - Run the database migration:
     ```
     flask db upgrade
     ```

5. Run the application:
   - Replit automatically sets up the run command in the `.replit` file.
   - Click the "Run" button to start the application.

6. Access your deployed application:
   - Replit provides a unique URL for your application.
   - Click on the URL at the top of the Replit window to open your deployed app.

## Data Access and Management

1. Database access:
   - The application uses a PostgreSQL database provided by Replit.
   - Database credentials are automatically set as environment variables.
   - Use these variables in your application to connect to the database:
     - `PGDATABASE`
     - `PGUSER`
     - `PGPASSWORD`
     - `PGHOST`
     - `PGPORT`

2. Superuser creation:
   - The first user to register becomes a superuser.
   - Superusers can invite and manage other superusers through the admin panel.

3. Data backup:
   - Regularly backup your database using Replit's built-in database tools.
   - Export your database periodically for off-site backups.

4. Scaling:
   - Replit handles most scaling issues automatically.
   - For high-traffic scenarios, consider upgrading your Replit plan.

5. Monitoring:
   - Use Replit's built-in logs to monitor application performance and errors.
   - Implement additional logging in your application for detailed tracking.

6. Security:
   - Keep your Replit account secure with a strong password and two-factor authentication.
   - Regularly update your application dependencies to patch security vulnerabilities.
   - Use HTTPS for all communications (Replit provides this by default).

7. Maintenance:
   - Regularly check for updates to Flask and other dependencies.
   - Test updates in a separate development environment before applying to production.

By following these guidelines, you can successfully deploy and manage the Temple Sponsor Management application in a production environment on Replit.
