from app import app, db
from flask_migrate import Migrate, upgrade

migrate = Migrate(app, db)

@app.cli.command("db_upgrade")
def db_upgrade():
    """Run database migrations."""
    upgrade()

if __name__ == "__main__":
    app.run(debug=True)
