"""Consistent database/media bundles. Restoration only targets a new offline directory."""
from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import zipfile

from django.conf import settings
from django.db import connection

from .media_lifecycle import MANAGED_NAME, media_lock


def database_dump(path):
    config = connection.settings_dict
    if connection.vendor == "sqlite":
        # A separate reader can snapshot while the media-lock transaction holds
        # SQLite's RESERVED writer lock. Never use backup() on that same writer.
        source_name = str(config["NAME"])
        if source_name == ":memory:" or source_name.startswith("file:memory"):
            raise ValueError("Use a file database for backup.")
        with closing(sqlite3.connect(source_name)) as source, closing(sqlite3.connect(path)) as target:
            source.backup(target)
        return "sqlite"
    if connection.vendor != "postgresql":
        raise ValueError("Unsupported database engine.")
    env = dict(os.environ)
    env.update(PGPASSWORD=str(config.get("PASSWORD", "")), PGCONNECT_TIMEOUT="5")
    options = config.get("OPTIONS", {})
    env["PGSSLMODE"] = options.get("sslmode", "prefer")
    if options.get("sslrootcert"):
        env["PGSSLROOTCERT"] = options["sslrootcert"]
    args = [settings.PG_DUMP_PATH, "--format=custom", "--no-owner", "--no-acl"]
    for option, key in (("--host", "HOST"), ("--port", "PORT"), ("--username", "USER")):
        if config.get(key):
            args.extend([option, str(config[key])])
    args.extend(["--dbname", str(config["NAME"])])
    with open(path, "wb") as stream:
        result = subprocess.run(args, env=env, stdout=stream, stderr=subprocess.PIPE, timeout=300)
    if result.returncode:
        raise ValueError("Database dump failed. Check client version and connection.")
    return "postgresql"


def create_backup(destination):
    destination = Path(destination)
    root = Path(settings.MEDIA_ROOT).resolve()
    if not destination.is_absolute() or destination.resolve().is_relative_to(root):
        raise ValueError("Choose an absolute backup destination outside MEDIA_ROOT.")
    if not root.is_dir():
        raise ValueError("MEDIA_ROOT is missing.")
    # Reference changes, file publishing and deletion use this same lock.
    with media_lock(), tempfile.TemporaryDirectory(prefix="library-backup-") as work:
        dump = Path(work) / "database"
        engine = database_dump(dump)
        db_name = "database.sqlite3" if engine == "sqlite" else "database.dump"
        entries = [(db_name, dump)]
        covers = root / "covers"
        if covers.exists():
            if covers.is_symlink():
                raise ValueError("Symlink media directories are unsupported.")
            for file in sorted(covers.iterdir()):
                name = "covers/" + file.name
                if file.is_symlink():
                    raise ValueError("Symlink media files are unsupported.")
                if file.is_file() and MANAGED_NAME.fullmatch(name):
                    entries.append(("media/" + name, file))
        # Refuse a backup that would silently omit a referenced legacy file.
        from .models import Book, CoverOperation
        pending = set(CoverOperation.objects.filter(kind="WRITE").values_list("name", flat=True))
        for name in Book.objects.exclude(cover="").values_list("cover", flat=True):
            if not MANAGED_NAME.fullmatch(name) or not ((root / name).is_file() or name in pending):
                raise ValueError("A referenced cover is missing or unmanaged.")
        manifest = {"version": 1, "engine": engine, "files": {}}
        created = False
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
            with os.fdopen(fd, "wb") as stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for name, file in entries:
                    digest = sha256()
                    with file.open("rb") as source, bundle.open(name, "w") as target:
                        while chunk := source.read(1024 * 1024):
                            digest.update(chunk)
                            target.write(chunk)
                    manifest["files"][name] = digest.hexdigest()
                bundle.writestr("manifest.json", json.dumps(manifest))
                bundle.close()
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise


def restore_backup(archive_path, target, max_bytes=2 * 1024**3):
    target = Path(target)
    if not target.is_absolute() or target.exists():
        raise ValueError("Restore target must be a new absolute directory.")
    stage = Path(tempfile.mkdtemp(prefix=".library-restore-", dir=target.parent))
    try:
        with zipfile.ZipFile(archive_path) as bundle:
            names = bundle.namelist()
            if len(names) != len(set(names)) or "manifest.json" not in names:
                raise ValueError("Invalid backup entries.")
            infos = bundle.infolist()
            if sum(item.file_size for item in infos) > max_bytes or bundle.getinfo("manifest.json").file_size > 1024 * 1024:
                raise ValueError("Backup exceeds restore size limit.")
            manifest = json.loads(bundle.read("manifest.json"))
            if not isinstance(manifest, dict) or manifest.get("version") != 1 or manifest.get("engine") not in {"sqlite", "postgresql"}:
                raise ValueError("Unsupported backup format.")
            files = manifest.get("files")
            if not isinstance(files, dict) or set(files) != set(names) - {"manifest.json"}:
                raise ValueError("Manifest does not match backup.")
            database = "database.sqlite3" if manifest["engine"] == "sqlite" else "database.dump"
            if database not in files:
                raise ValueError("Database dump missing.")
            for name, expected in files.items():
                if name != database and not (name.startswith("media/") and MANAGED_NAME.fullmatch(name[6:])):
                    raise ValueError("Unsafe backup entry.")
                if (bundle.getinfo(name).external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlinks are not allowed.")
                output = stage / name
                output.parent.mkdir(parents=True, exist_ok=True)
                digest = sha256()
                with bundle.open(name) as source, output.open("xb") as destination:
                    os.chmod(output, 0o600)
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        destination.write(chunk)
                if digest.hexdigest() != expected:
                    raise ValueError("Backup checksum mismatch.")
            (stage / "manifest.json").write_text(json.dumps(manifest))
        if manifest["engine"] == "sqlite":
            with closing(sqlite3.connect(f"file:{stage / database}?mode=ro", uri=True)) as db:
                if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("Invalid SQLite snapshot.")
        else:
            with (stage / database).open("rb") as dump:
                if dump.read(5) != b"PGDMP":
                    raise ValueError("Invalid PostgreSQL custom dump.")
        # Refuse to replace any target that appeared during validation.
        target.mkdir(mode=0o700)
        try:
            for item in stage.iterdir():
                shutil.move(str(item), target / item.name)
        except BaseException:
            shutil.rmtree(target)
            raise
        return manifest["engine"]
    finally:
        shutil.rmtree(stage, ignore_errors=True)
