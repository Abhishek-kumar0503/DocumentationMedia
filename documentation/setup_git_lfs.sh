#!/bin/bash

# Install Git LFS
echo "Installing Git LFS..."
sudo apt-get install git-lfs -y

# Navigate to the startup directory (correct repository root)
cd /home/hope/Desktop/startup

# Create directory structure if it doesn't exist
mkdir -p documentation/media_uploads/documentation

# Create .gitattributes file in documentation folder
echo "Creating .gitattributes file..."
cat > documentation/.gitattributes << EOF
# Git LFS tracking for large files
media_uploads/documentation/*.txt filter=lfs diff=lfs merge=lfs -text
media_uploads/documentation/*.pdf filter=lfs diff=lfs merge=lfs -text
media_uploads/documentation/*.docx filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
EOF

# Initialize Git if not already initialized
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
fi

# Initialize Git LFS
git lfs install

# Track large files
git lfs track "documentation/media_uploads/documentation/*.txt"
git lfs track "documentation/media_uploads/documentation/*.pdf"
git lfs track "documentation/media_uploads/documentation/*.docx"
git lfs track "documentation/*.mp4"
git lfs track "documentation/*.zip"

# Add root .gitattributes
git add .gitattributes

# Add documentation .gitattributes if it exists
if [ -f documentation/.gitattributes ]; then
    git add documentation/.gitattributes
fi

# Add GitHub remote if not present
if ! git remote | grep -q "origin"; then
    echo "Adding GitHub remote repository..."
    git remote add origin https://github.com/Abhishek-kumar0503/DocumentationMedia.git
else
    echo "Setting GitHub remote repository URL..."
    git remote set-url origin https://github.com/Abhishek-kumar0503/DocumentationMedia.git
fi

# Stage everything in documentation/ directory
echo "Adding documentation files to Git..."
git add documentation/

# Commit
echo "Committing changes..."
git commit -m "Add documentation files with Git LFS support"

# Push - use main or master branch depending on what exists
echo "Pushing to GitHub repository..."
if git show-ref --verify --quiet refs/heads/main; then
    git push -u origin main
else
    git push -u origin master
fi

echo "✅ Git LFS setup complete and documentation pushed to GitHub."
echo "Repository URL: https://github.com/Abhishek-kumar0503/DocumentationMedia"
