#!/bin/bash

echo "Checking if a compatible Python version is installed..."
python_ver=$(python3 --version)
case "$python_ver" in
    "Python 3.10."*|"Python 3.13."*)
        echo "✅ Compatible Python version found - ("$python_ver")"
        ;;
    *)
        echo "❌ No compatible Python version found. Must have Python 3.10.x or Python 3.13.x installed."
        ;;
esac

# save locally installed packages into a temp file, normalize package names to match requirements.txt
pip list --format=freeze | sed 's/-/_/g' > locally_installed.txt
key_file="requirements.txt"
compare_file="locally_installed.txt"

missing_packages=0
to_install=()

while IFS= read -r line; do
  if ! grep -iFxq "$line" "$compare_file"; then
    echo "❌ Missing package in locally installed packages: $line"
    ((missing_packages++))
    to_install+="$line"
  fi
done < "$key_file"

if [[ $missing_packages -eq 0 ]]; then
  echo "✅ All packages from $key_file are present in locally installed Python packages"
else
  echo "⚠️  $missing_packages package(s) missing from $key_file"
  echo "Install missing packages ($missing_packages)?"
  read package_resp
  if [[ $package_resp == "Y" || $package_resp == 'y' ]]; then  # broken here
    echo "Installing packages ($missing_packages)..."
    # check if virtual environment exists, if not create it
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    # enable virtual environment
    source .venv/bin/activate
    for i in "$to_install"
      do
          
          # install package
          install_cmd=$(pip install "$i")
          echo "$install_cmd"
      done
fi

# clean up temp files
rm locally_installed.txt