#!/usr/bin/python
#
# Setup Settings
#
#=============================================================================#
# Imports
#=============================================================================#

# System Modules
import os
import sys
import glob
import json

# Custom Modules
import click
from send2trash import send2trash  # https://github.com/hsoft/send2trash

#=============================================================================#
# Functions
#=============================================================================#

def symlink(cur, json, src, dst, title, overwrite=False):

    # Grab the full source path from the json file and append the parent dir
    json = os.path.dirname(json)
    src = json + "/" + src

    dst = os.path.expanduser(dst)

    # Check if the source file exists
    if not any([
            os.path.isfile(src),
            os.path.isdir(src),
            os.path.islink(src)]
            ):
        click.echo("ERROR: The requested source doesnt exist",err)
        click.echo(title)
        click.echo(src)
        return

    # Prompt the User to either overwrite existing files or skip them
    if any([
        os.path.isfile(dst),
        os.path.isdir(dst),
        os.path.islink(dst)]
            ):

            if not overwrite:

                prompt = ""

                click.echo("File " + dst + " already exists.")

                # Overwrite Prompt
                #
                # a: Overwrite all files and don't ask anymore
                # y: Continue the symlink function and overwrite
                # n: Exit the symlink function and don't overwrite
                #
                # On any other input repeat the prompt
                while all([
                    prompt != "y",
                    prompt != "n",
                    prompt != "a"
                        ]):

                    prompt = raw_input("Overwrite (y/n/a): ")

                    if (prompt == "a"):
                        overwrite = True  # Overwrite All
                    elif (prompt == "n"):
                        overwrite = False
                        return   # Exit
                    elif (prompt == "y"):
                        pass   # Overwrite only this file

    # Trash the existing destination if available and symlink the source
    trash(dst)
    os.symlink(src, dst)

    return overwrite


def trash(dst):

    """Moves given Objects to trash or unlinks symlinks"""

    if any([os.path.isfile(dst), os.path.isdir(dst)]):
        send2trash(dst)
    elif os.path.islink(dst):
        os.unlink(dst)

#=============================================================================#
# Main
#=============================================================================#

@click.command()
@click.option('--test', is_flag=True, help="Testing Mode")
@click.option('--cfg_file', default="sync_settings.json", 
              help="Alternate name for the configuration file")
@click.option('--overwrite', default=False, is_flag=True,
              help="Overwrite all files")
def cli(test, cfg_file, overwrite):

    """Synchronize Settings will synchronize your app Settings according to a sync_settings.json"""

    # Path with the settings
    settings_dir = "~/Settings"
    settings_dir = os.path.expanduser(settings_dir)

    # Check if there is either a symlink or a dir ~/Settings
    # After that check if there is a Settings dir in the root dir of the script
    # If none of these exist, exit the script
    if (os.path.islink(settings_dir)):
        # Expand the user and find the symlink target path
        settings_dir = (os.path.realpath(os.path.expanduser(settings_dir)))
    elif (os.path.isdir(settings_dir)):
        # Expand the user and find the symlink target path
        settings_dir = (os.path.expanduser(settings_dir))
    else:
        print "No Settings folder found in either ~/ or the script dir!"
        return

      # Get all sync setting files
      # Or just the test folder in test mode
    if test:
        cfg = [settings_dir + '/test/' + cfg_file]
    else:
        # TODO 002: Replace this with a walk function
        cfg = glob.glob(settings_dir + '*/' + cfg_file)
        cfg += glob.glob(settings_dir + '*/*/' + cfg_file)
        cfg += glob.glob(settings_dir + '*/*/*/' + cfg_file)
        cfg += glob.glob(settings_dir + '*/*/*/*/' + cfg_file)

    # If there aren't any config files exit the script
    if not(cfg):
        print ("No %s files found!" % cfg_file)
        return

    #-------------------------------------------------------------------------#
    # Symlink Iteration
    #-------------------------------------------------------------------------#

    # Loop through the configuration files and create the symlinks
    for x in cfg:

        # Load the data from the json files into data
        json_data = open(x)
        data = json.load(json_data)
        json_data.close()

        # Get the folders to trash if they are available
        if "trash" in data:
            for t in data["trash"]:
                trash(t)

        if "symlink" in data:
            for d in data["symlink"]:

                overwrite = symlink(
                    settings_dir,
                    x,
                    d["src"], d["dst"],
                    d["title"],
                    overwrite)
