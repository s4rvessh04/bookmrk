import subprocess
from pathlib import Path
from time import sleep
import pkg_resources

import click
from tinydb import TinyDB, Query
from rich.console import Console
from rich.style import Style

db = TinyDB(Path(__file__).absolute().parent / "db.json")
q = Query()
console = Console()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    
    version = pkg_resources.get_distribution("bookmrk").version
    console.print(f"bookmrk version {version}")
    ctx.exit()


@click.group()
@click.option("-v", "--version", is_flag=True, help="Show the version and exit.", callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass


@cli.command(help="Open the bookmark.")
@click.option("-n", "--name", required=True, prompt="Name", help="The name of the bookmark.")
def open(name: str):
    if db.contains(q.name == name.lower()) is False:
        console.print(":cross_mark:", "Bookmark not found!", style="red")
        return
    
    with console.status("Opening bookmark..."):
        sleep(0.5)
        query = db.get(q.name == name).get("path")
        path = Path(query).resolve()
        console.print(":file_folder:", path, style=Style(color="magenta", link=path))
        subprocess.Popen(["explorer", path], shell=True)
        return path


@cli.command(help="Add a bookmark.")
@click.option("-n", "--name", required=True, prompt="Name", help="The name of the bookmark.")
@click.option("-p", "--path", required=True, prompt="Path", help="The path for the bookmark.")
def add(name: str, path: str):
    path_obj = Path(path).resolve()

    if db.contains(q.name == name.lower()) or db.contains(q.path == path_obj.absolute().as_posix()):
        console.print(":construction:", "Bookmark already exists!", style="yellow")
        return
    

    if not path_obj.exists():
        console.print(":paw_prints:", "Path does not exist!", style="red")
        return
    
    with console.status("Adding bookmark..."):
        sleep(0.5)
        db.insert({"name": name.lower(), "path": path_obj.absolute().as_posix()})
        console.print(":raising_hands:", "Added", style="green")


@cli.command(help="List all bookmarks.")
def list():
    with console.status("Listing all bookmarks..."):
        sleep(0.5)
        bookmarks = db.all()
        for bookmark in bookmarks:
            console.print(bookmark)
        console.print(":file_cabinet:", "Total bookmarks: " + str(len(bookmarks)))


@cli.command(help="Find a bookmark.")
@click.option("--path", is_flag=True, help="Get a bookmark's path.")
@click.argument("name")
def find(name, path):
    items = db.search(q.name == name)
    if len(items) == 0:
        console.print(":cross_mark:", "No bookmarks found!", style="red")
        return
    
    with console.status("Finding bookmark..."):
        sleep(0.5)
        for bookmark in items:
            if path:
                link = bookmark.get("path")
                console.print(":file_folder:", link, style=Style(color="magenta", link=link))
            else:
                console.print(bookmark)


def validate_exist(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    if not db.contains(q.name == value.lower()):
        console.print(":cross_mark:", "Bookmark not found!", style="red")
        ctx.exit()
    return value


@cli.command(help="Update a bookmark.")
@click.option("-n", "--name", required=True, prompt="Name", help="The name of the bookmark.", callback=validate_exist)
@click.option("-nn", "--new-name", prompt="New name", default="DEFAULT", help="The new name for the bookmark.")
@click.option("-np", "--new-path", prompt="New path", default="DEFAULT", help="The new path for the bookmark.")
def update(name: str, new_name: str, new_path: str):
    bookmark = db.get(q.name == name)
    update_fields = {"name": bookmark.get("name"), "path": bookmark.get("path")}
    
    if new_name == "DEFAULT" and new_path == "DEFAULT":
        console.print(":construction:", "Nothing to update.", style="yellow")
        return
    if new_name != "DEFAULT":
        if db.contains(q.name == new_name.lower()):
            console.print(":construction:", f"Bookmark already exists for name=\"{name}\"!", style="yellow")
            return
        update_fields["name"] = new_name.lower()
    if new_path != "DEFAULT":
        resolved_path = Path(new_path).expanduser().resolve()
        new_path = resolved_path.absolute().as_posix()
        if db.contains(q.path == new_path):
            console.print(":construction:", f"Bookmark already exists for path=\"{new_path}\"!", style=Style(color="yellow"))
            return
        if resolved_path.exists():
            update_fields["path"] = new_path
        else:
            console.print(":paw_prints:", "Path does not exist!", style="red")
            return
    
    with console.status("Updating bookmark..."):
        sleep(0.5)
        db.update(update_fields, q.name == name)
        console.print(":raising_hands:", "Updated", style="green")


@cli.command(help="Remove a bookmark.")
@click.option("-n", "--name", required=False, help="The name of the bookmark", callback=validate_exist)
@click.option("--all", is_flag=True, help="Remove all bookmarks.")
def remove(name: str, all: bool):
    if all and name:
        console.print(":construction:", "You can't use --all and a name at the same time", style="yellow")
        return
    if all:
        choices = click.Choice(["y", "N"])
        confirmation = click.prompt(type=choices, text="Are you sure you want to remove all bookmarks?")

        if confirmation == "y":
            with console.status("Removing bookmarks..."):
                sleep(0.5)
                db.truncate()
                console.print(":rotating_light:", "Removed all bookmarks", style="red")
        elif confirmation == "N":
            console.print(":construction:", "Cancelled", style="yellow")

        return
    
    with console.status("Removing bookmark..."):
        sleep(0.5)
        db.remove(q.name == name), name
        console.print(":raising_hands:", "Removed", style="green")