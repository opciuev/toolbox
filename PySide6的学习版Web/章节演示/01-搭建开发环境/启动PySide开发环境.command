#!/bin/zsh

script_dir="${0:A:h}"
venv_activate="$script_dir/.venv/bin/activate"

if [[ -f "$venv_activate" ]]; then
  source "$venv_activate"
  echo "已启用：$venv_activate"
else
  echo "未找到 $venv_activate，将使用当前 Python 环境。"
fi

if command -v code >/dev/null 2>&1; then
  code "$script_dir"
else
  open -a "Visual Studio Code" "$script_dir"
fi
