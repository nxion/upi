#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Post installation script for  Ubuntu 16.04
#
# Syntax: sudo ./ubuntupostinstall-16.04.sh
#

__appname__ = 'ubuntu-16.04-postinstall'
__version__ = "0.1"
__author__ = "Nxion"
__licence__ = "LGPL"

"""
Post installation script for Ubuntu 16.04
"""

import os
import sys
import platform
import getopt
import shutil
import logging
import getpass
import ConfigParser
import gettext
gettext.install(__appname__)

# Global variables
#-----------------------------------------------------------------------------

_FOR_UBUNTU = "xenial"
_DEBUG = 1
_LOG_FILE = "/tmp/%s.log" % __appname__
_CONF_FILE = "https://raw.github.com/nxion/upi/master/ubuntu-16.04-i3-postinstall.cfg"

# System commands
#-----------------------------------------------------------------------------

_APT_ADD = "add-apt-repository -y"
_APT_INSTALL = "DEBIAN_FRONTEND=noninteractive apt -y -f install"
_APT_REMOVE = "DEBIAN_FRONTEND=noninteractive apt -y -f remove"
_APT_UPDATE = "DEBIAN_FRONTEND=noninteractive apt -y update"
_APT_UPGRADE = "DEBIAN_FRONTEND=noninteractive apt -y upgrade"
_APT_KEY = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys"
_WGET = "/usr/bin/wget"

# Classes
#-----------------------------------------------------------------------------

class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ORANGE = '\033[93m'
    NO = '\033[0m'

    def disable(self):
        self.RED = ''
        self.GREEN = ''
        self.BLUE = ''
        self.ORANGE = ''
        self.NO = ''

# Functions
#-----------------------------------------------------------------------------


def init():
    """
    Init the script
    """
    # Globals variables
    global _VERSION
    global _DEBUG

    # Set the log configuration
    logging.basicConfig( \
        filename=_LOG_FILE, \
        level=logging.DEBUG, \
        format='%(asctime)s %(levelname)s - %(message)s', \
         datefmt='%d/%m/%Y %H:%M:%S', \
     )


def syntax():
    """
    Print the script syntax
    """
    print(_("Ubuntu 16.04 post installation script version %s for %s")
                                            % (__version__, _FOR_UBUNTU))
    print("")
    print(_("Syntax: %s.py [-c cfgfile] [-h] [-v]") % __appname__)
    print(_("  -c cfgfile: Use the cfgfile instead of the default one"))
    print(_("  -h        : Print the syntax and exit"))
    print(_("  -v        : Print the version and exit"))
    print(_(""))
    print(_("Examples:"))
    print(_(""))
    print(_(" # %s.py") % __appname__)
    print(_(" > Run the script with the default configuration file"))
    print(_("   %s") % _CONF_FILE)
    print("")
    print(_(" # %s.py -c ./myconf.cfg") % __appname__)
    print(_(" > Run the script with the ./myconf.cfg file"))
    print("")
    print(_(" # %s.py -c http://mysite.com/myconf.cfg") % __appname__)
    print(_(" > Run the script with the http://mysite.com/myconf.cfg configuration file"))
    print("")


def version():
    """
    Print the script version
    """
    sys.stdout.write(_("Script version %s") % __version__)
    sys.stdout.write(_(" (running on %s %s)\n") % (platform.system(), platform.machine()))


def isroot():
    """
    Check if the user is root
    Return TRUE if user is root
    """
    return (os.geteuid() == 0)


def showexec(description, command, exitonerror = 0, presskey = 0, waitmessage = ""):
    """
    Exec a system command with a pretty status display (Running / Ok / Warning / Error)
    By default (exitcode=0), the function did not exit if the command failed
    """

    if _DEBUG:
        logging.debug("%s" % description)
        logging.debug("%s" % command)

    # Wait message
    if (waitmessage == ""):
        waitmessage = description

    # Manage very long description
    if (len(waitmessage) > 65):
        waitmessage = waitmessage[0:65] + "..."
    if (len(description) > 65):
        description = description[0:65] + "..."

    # Display the command
    if (presskey == 1):
        status = _("[ ENTER ]")
    else:
        status = _("[Running]")
    statuscolor = colors.BLUE
    sys.stdout.write (colors.NO + "%s" % waitmessage + statuscolor + "%s" % status.rjust(79-len(waitmessage)) + colors.NO)
    sys.stdout.flush()

    # Wait keypressed (optionnal)
    if (presskey == 1):
        try:
            input = raw_input
        except:
            pass
        raw_input()

    # Run the command
    returncode = os.system ("/bin/sh -c \"%s\" >> /dev/null 2>&1" % command)
    # returncode = os.system ("\"%s\" >> /dev/null 2>&1" % command)
    # test switching os.system for subprocess
    # returncode = subprocess.call ("/bin/sh" +  "-c \"%s\" >> /dev/null 2>&1" % command, shell=True)

    # Display the result
    if ((returncode == 0) or (returncode == 25600)):
        status = "[  OK   ]"
        statuscolor = colors.GREEN
    else:
        if exitonerror == 0:
            status = "[Warning]"
            statuscolor = colors.ORANGE
        else:
            status = "[ Error ]"
            statuscolor = colors.RED

    sys.stdout.write (colors.NO + "\r%s" % description + statuscolor + "%s\n" % status.rjust(79-len(description)) + colors.NO)

    if _DEBUG:
        logging.debug (_("Returncode = %d") % returncode)

    # Stop the program if returncode and exitonerror != 0
    if ((returncode != 0) & (exitonerror != 0)):
        if _DEBUG:
            logging.debug (_("Forced to quit"))
        exit(exitonerror)


def getpassword(description = ""):
    """
    Read password (with confirmation)
    """
    if (description != ""):
        sys.stdout.write ("%s\n" % description)

    password1 = getpass.getpass(_("Password: "));
    password2 = getpass.getpass(_("Password (confirm): "));

    if (password1 == password2):
        return password1
    else:
        sys.stdout.write (colors.ORANGE + _("[Warning] Password did not match, please try again") + colors.NO + "\n")
        return getpassword()


def getstring(message = _("Enter a value: ")):
    """
    Ask user to enter a value
    """
    try:
        input = raw_input
    except:
        pass
    return raw_input(message)


def waitenterpressed(message = _("Press ENTER to continue...")):
    """
    Wait until ENTER is pressed
    """
    try:
        input = raw_input
    except:
        pass
    raw_input(message)
    return 0


def main(argv):
    """
    Main function
    """
    try:
        opts, args = getopt.getopt(argv, "c:hv", ["config", "help", "version"])
    except getopt.GetoptError:
        syntax()
        exit(2)

    config_file = ""
    config_url = _CONF_FILE
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            if arg.startswith("http://") or \
                arg.startswith("https://") or \
                arg.startswith("ftp://"):
                config_url = arg
            else:
                config_file = arg
        elif opt in ("-h", "--help"):
            syntax()
            exit()
        elif opt in ('-v', "--version"):
            version()
            exit()

    # Are your root ?
    if (not isroot()):
        showexec (_("Script should be run as root"), "tpastroot", exitonerror = 1)

    # Is it Precise Pangolin ?
    _UBUNTU_VERSION = platform.linux_distribution()[2]
    if (_UBUNTU_VERSION != _FOR_UBUNTU):
        showexec (_("Script only for Ubuntu %s") % _FOR_UBUNTU, "badubuntuversion", exitonerror = 1)

    # Read the configuration file
    if (config_file == ""):
        config_file = "/tmp/%s.cfg" % __appname__
        showexec (_("Download the configuration file"), "rm -f "+config_file+" ; "+_WGET+" -O "+config_file+" "+config_url)
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    # Parse and exec pre-actions
    for action_name, action_cmd in config.items("preactions"):
        showexec (_("Execute preaction ")+action_name.lstrip("action_"), action_cmd)

    # Update repos
    showexec (_("Update repositories"), _APT_UPDATE)

    # Upgrade system
    showexec (_("System upgrade (~20 mins, please be patient...)"), _APT_UPGRADE)

    # Parse and install packages
    for pkg_type, pkg_list in config.items("packages"):
        if (pkg_type.startswith("remove_")):
            showexec (_("Remove packages ")+pkg_type.lstrip("remove_"), _APT_REMOVE+" "+pkg_list)
        else:
            showexec (_("Install packages ")+pkg_type, _APT_INSTALL+" "+pkg_list)

   
    '''
    I needed to comment out all the dotfiles peices because of issues with os.system. You can
    look at the issues section to see why it is an issue. os.system is outdated and should be 
    replaced with subprocess. I will work on that, until then this script now works.
    '''
    # # Install packages related to repositories
    # #~ print pkg_list_others
    # for pkg in pkg_list_others.keys():
    #     showexec (_("Install packages ")+pkg, _APT_INSTALL+" "+pkg_list_others[pkg])

    # # Allow user to read DVD (CSS)
    # showexec (_("DVDs CSS encryption reader"), "sh /usr/share/doc/libdvdread4/install-css.sh")

    # Download and install dotfiles: vimrc, prompt...
   # if (config.has_section("dotfiles")):
        # Create the bashrc.d subfolder
        #showexec (_("Create the ~/.bashrc.d subfolder"), "mkdir -p $HOME/.bashrc.d")
        #if (config.has_option("dotfiles", "bashrc")):
        #    showexec (_("Download bash main configuration file"), _WGET+" -O $HOME/.bashrc "+config.get("dotfiles", "bashrc"))
        #if (config.has_option("dotfiles", "bashrc_prompt")):
        #    showexec (_("Download bash prompt configuration file"), _WGET+" -O $HOME/.bashrc.d/bashrc_prompt "+config.get("dotfiles", "bashrc_prompt"))
        #if (config.has_option("dotfiles", "bashrc_aliases")):
        #    showexec (_("Download bash aliases configuration file"), _WGET+" -O $HOME/.bashrc.d/bashrc_aliases "+config.get("dotfiles", "bashrc_aliases"))
        #showexec (_("Install the bash configuration file"), "chown -R $me:$me $HOME/.bashrc*")
        # Vim
        #if (config.has_option("dotfiles", "vimrc")):
         #   showexec (_("Donwload the Vim configuration file"), _WGET+" -O $HOME/.vimrc "+config.get("dotfiles", "vimrc"))
          #  showexec (_("Install the Vim configuration file"), "chown -R $me:$me $HOME/.vimrc")

        # Htop
        #if (config.has_option("dotfiles", "htoprc")):
         #   showexec (_("Download the Htop configuration file"), _WGET+" -O $HOME/.htoprc "+config.get("dotfiles", "htoprc"))
          #  showexec (_("Install the Htop configuration file"), "chown -R $me:$me $HOME/.htoprc")

        # Xresources
        #if (config.has_option("dotfiles", "xres")):
         #   showexec(_("Downloading the Xresources file"), _WGET+"-O $HOME/.Xresources "+config.get("dotfiles", "xres"))
          #  showexec(_("Installing the Xresources file"), "chown -R me:me $HOME/.Xresources")

        # xinitrc
        #if (config.has_option("dotfiles", "xinit")):
        #    showexec(_("Downloading the xinitrc file"), _WGET+"-O $HOME/.xinitrc "+config.get("dotfiles", "xres"))
         #   showexec(_("Installing the xinitrc file"), "chown -R me:me $HOME/.xinitrc"

    # Parse and exec post-actions
    for action_name, action_cmd in config.items("postactions"):
        showexec (_("Execute postaction ")+action_name.lstrip("action_"), action_cmd)

    # End of the script
    print("---")
    print(_("End of the script."))
    print(_(" - Cfg file: ")+config_file)
    print(_(" - Log file: ")+_LOG_FILE)
    print("")
    print(_("Please restart your session to complete."))
    print("---")

# Main program
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    init()
    main(sys.argv[1:])
    exit()
