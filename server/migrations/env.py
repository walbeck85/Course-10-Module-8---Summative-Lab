from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. --- OUR CUSTOM IMPORTS ---
from server.models import db
from server.config import app
# ------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 2. --- OUR CUSTOM APP CONTEXT ---
with app.app_context():
    # ------------------------------------

    # 3. --- FIX 1: Comment out logging ---
    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    # if config.config_file_name is not None:
    #     fileConfig(config.config_file_name)
    # ------------------------------------

    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata

    # 4. --- FIX 2: Set target_metadata ---
    target_metadata = db.metadata
    # --------------------------------

    def run_migrations_offline() -> None:
        """Run migrations in 'offline' mode.
        """
        # 5. --- FIX 3: Set URL for offline mode ---
        # url = config.get_main_option("sqlalchemy.url")
        url = app.config['SQLALCHEMY_DATABASE_URI']
        # -------------------------------------------
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


    def run_migrations_online() -> None:
        """Run migrations in 'online' mode.
        """

        # 6. --- FIX 4: Set URL for online mode ---
        config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
        # ----------------------------------------

        # 7. --- FIX 5: Use config_ini_section ---
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}), # Use _ini_ section
            prefix="sqlalchemy.",
            poolclass=pool.QueuePool,
        )
        # --------------------------------------

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()