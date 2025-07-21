#!/bin/bash
# Release script for Field Coverage Planner
# Usage: ./release.sh <version> [--dry-run]

set -e

VERSION=$1
DRY_RUN=$2

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version required"
    echo "Usage: ./release.sh <version> [--dry-run]"
    echo "Example: ./release.sh v1.1.0"
    exit 1
fi

# Ensure version starts with 'v'
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Version must be in format vX.Y.Z (e.g., v1.1.0)"
    exit 1
fi

echo "🚀 Preparing release $VERSION"

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory is not clean"
    echo "Please commit or stash your changes first"
    git status --short
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main branch (currently on $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update version in setup.py if needed
if grep -q "version=" setup.py; then
    SETUP_VERSION=$(echo $VERSION | sed 's/^v//')
    echo "📝 Updating setup.py version to $SETUP_VERSION"
    if [ "$DRY_RUN" != "--dry-run" ]; then
        sed -i.bak "s/version=\"[^\"]*\"/version=\"$SETUP_VERSION\"/" setup.py
        rm setup.py.bak 2>/dev/null || true
    fi
fi

# Run compatibility check
echo "🔍 Running compatibility check..."
if [ "$DRY_RUN" != "--dry-run" ]; then
    python3 tests/check_compatibility.py
    if [ $? -ne 0 ]; then
        echo "❌ Compatibility check failed"
        exit 1
    fi
fi

# Run tests if they exist
if [ -f "tests/test_basic.py" ]; then
    echo "🧪 Running tests..."
    if [ "$DRY_RUN" != "--dry-run" ]; then
        python3 -m pytest tests/ -v
        if [ $? -ne 0 ]; then
            echo "❌ Tests failed"
            exit 1
        fi
    fi
fi

# Create release notes template
RELEASE_NOTES_FILE="release_notes_$VERSION.md"
echo "📝 Creating release notes template: $RELEASE_NOTES_FILE"

if [ "$DRY_RUN" != "--dry-run" ]; then
    cat > "$RELEASE_NOTES_FILE" << EOF
# Release $VERSION

## 🎯 Overview
Brief description of this release...

## ✨ New Features
- Feature 1
- Feature 2

## 🛠️ Improvements  
- Improvement 1
- Improvement 2

## 🐛 Bug Fixes
- Fix 1
- Fix 2

## 📚 Documentation
- Documentation updates

## 🧪 Testing
- Test improvements

## ⚠️ Breaking Changes
- None / List any breaking changes

## 📦 Installation
\`\`\`bash
git clone https://github.com/SDNT8810/field-coverage-planner.git
cd field-coverage-planner
git checkout $VERSION
pip install -r requirements.txt
python3 run.py --help
\`\`\`

## 🔄 Upgrade Instructions
\`\`\`bash
git pull origin main
git checkout $VERSION
pip install -r requirements.txt --upgrade
\`\`\`
EOF
    echo "✅ Please edit $RELEASE_NOTES_FILE with actual release notes"
    echo "Press Enter when ready to continue..."
    read
fi

# Commit version changes if any
if [ "$DRY_RUN" != "--dry-run" ] && [ -n "$(git status --porcelain)" ]; then
    echo "📝 Committing version updates..."
    git add .
    git commit -m "Bump version to $VERSION"
fi

# Create and push tag
echo "🏷️  Creating Git tag $VERSION"
if [ "$DRY_RUN" != "--dry-run" ]; then
    # Read release notes if file exists
    if [ -f "$RELEASE_NOTES_FILE" ]; then
        RELEASE_MESSAGE=$(cat "$RELEASE_NOTES_FILE")
    else
        RELEASE_MESSAGE="Release $VERSION"
    fi
    
    git tag -a "$VERSION" -m "$RELEASE_MESSAGE"
    echo "📤 Pushing tag to origin..."
    git push origin "$VERSION"
fi

echo "🎉 Release $VERSION prepared successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to GitHub: https://github.com/SDNT8810/Coverage_Path_Planning/releases"
echo "2. Create a new release from tag $VERSION"
echo "3. Copy release notes from $RELEASE_NOTES_FILE"
echo "4. Upload any release assets if needed"
echo "5. Publish the release"

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo ""
    echo "🔍 DRY RUN completed - no changes were made"
fi
