
############## INSTALLATION

# google chrome

# core
sudo apt install -y curl wget git

# zsh
sudo apt install -y zsh
chsh -s $(which zsh)

# oh-my-zsh
if ! [ -d "$HOME/.oh-my-zsh" ]; then
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# oh-my-zsh plugins
if ! [ -d "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
fi
if ! [ -d "$HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
fi

# tmux
sudo apt install tmux

# tmux plugin manager
if ! [ -d "$HOME/.tmux/plugins/tpm" ]; then
    git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
fi

# tmux - install plugins
$HOME/.tmux/plugins/tpm/bin/install_plugins

# tmux - create initial main session and save it
if [ ! -e "$HOME/.local/share/tmux/resurrect/last" ] && [ ! -e "$HOME/.tmux/resurrect/last" ]; then
    tmux new-session -d -s main
    tmux run-shell "$HOME/.tmux/plugins/tmux-resurrect/scripts/save.sh"
    tmux kill-session -t main
fi

# micro
sudo apt install -y micro

# keepassxc
if ! dpkg -l | grep keepassxc &> /dev/null; then
    sudo apt -y install keepassxc
fi

# obsidian
if ! snap list | grep obsidian &> /dev/null; then
    snap install obsidian --classic
fi

# spotify
if ! snap list | grep spotify &> /dev/null; then
    snap install spotify
fi

# claude desktop
if ! dpkg -l | grep -q claude-desktop &> /dev/null; then
    sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
    echo "deb [signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
    sudo apt update && sudo apt install claude-desktop
fi


############## SETUP


export DOTFILES=$HOME/repos/dotfiles

# clone dotfiles
if [ ! -d $DOTFILES ]; then
    mkdir -p ~/repos
    cd ~/repos
    git clone git@github.com:dsonyy/dotfiles.git
fi

# setup dot symlinks to ~
for f in "$DOTFILES"/dot/.[!.]* "$DOTFILES"/dot/*; do
    [ -e "$f" ] || continue
    ln -sf "$f" "$HOME/$(basename "$f")"
done

echo OK
