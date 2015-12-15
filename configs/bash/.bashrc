# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific aliases and functions
PATH=$HOME/.local/bin:$HOME/bin:$HOME/local/bin:$HOME/local/sbin:$PATH
export PATH

alias supervisorctl="supervisorctl -c $HOME/local/supervisor/supervisord.conf"