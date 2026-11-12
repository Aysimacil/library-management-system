from django.db import migrations


def install(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute("""
            CREATE FUNCTION books_guard_copy_history() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                IF NEW.book_id <> OLD.book_id AND EXISTS (
                    SELECT 1 FROM circulation_loan WHERE copy_id = OLD.id
                ) THEN
                    RAISE EXCEPTION 'A copy with loan history cannot change books'
                        USING ERRCODE = '23514';
                END IF;
                RETURN NEW;
            END; $$
        """)
        schema_editor.execute("""
            CREATE TRIGGER books_copy_history BEFORE UPDATE OF book_id ON books_bookcopy
            FOR EACH ROW EXECUTE FUNCTION books_guard_copy_history()
        """)
    elif vendor == "sqlite":
        schema_editor.execute("""
            CREATE TRIGGER books_copy_history BEFORE UPDATE OF book_id ON books_bookcopy
            WHEN NEW.book_id <> OLD.book_id AND EXISTS (
                SELECT 1 FROM circulation_loan WHERE copy_id = OLD.id
            )
            BEGIN SELECT RAISE(ABORT, 'A copy with loan history cannot change books'); END
        """)


def remove(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP TRIGGER books_copy_history ON books_bookcopy")
        schema_editor.execute("DROP FUNCTION books_guard_copy_history()")
    elif schema_editor.connection.vendor == "sqlite":
        schema_editor.execute("DROP TRIGGER books_copy_history")


class Migration(migrations.Migration):
    dependencies = [("books", "0001_initial"), ("circulation", "0001_initial")]
    operations = [migrations.RunPython(install, remove)]
