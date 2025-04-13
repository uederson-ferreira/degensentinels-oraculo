
# >>> conda initialize >>>

if [ -n "$CONDA_DEFAULT_ENV" ]; then
    conda deactivate
fi

# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Caminho para executáveis do sistema
export PATH=$PATH:/usr/local/bin

# Completar comandos do Stellar (mantendo apenas uma linha)
source <(stellar completion --shell zsh)

# Configuração do Go
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin


