#!/bin/bash

# Install Git LFS
echo "Installing Git LFS..."
sudo apt-get install git-lfs

# Navigate to your repository
cd /home/hope/Desktop/startup

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
git lfs track "*.mp4"
git lfs track "*.zip"

# Add .gitattributes file
git add .gitattributes

# Add remote repository if not already added
if ! git remote | grep -q "origin"; then
    echo "Adding GitHub remote repository..."
    git remote add origin https://github.com/Abhishek-kumar0503/DocumentationMedia.git
else
    echo "GitHub remote repository already configured."
fi

# Add all files in the documentation directory
echo "Adding documentation files to Git..."
git add documentation/

# Commit the changes
git commit -m "Add documentation files with Git LFS support"

# Push to GitHub
echo "Pushing to GitHub repository..."
git push -u origin main || git push -u origin master

echo "Git LFS setup complete. Documentation has been pushed to GitHub."
echo "Repository URL: https://github.com/Abhishek-kumar0503/DocumentationMedia"
