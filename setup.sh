#!/bin/bash

# GroundCrew Setup Script
echo "=========================================="
echo "GroundCrew Setup"
echo "=========================================="
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed."
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "✅ Poetry installed!"
    echo ""
    echo "⚠️  Please restart your shell or run:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    exit 0
fi

echo "✅ Poetry found: $(poetry --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f "env.template" ]; then
        echo "📝 Creating .env file from template..."
        cp env.template .env
        echo "✅ .env file created!"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
        echo "   - OPENAI_API_KEY=sk-your-key-here"
        echo "   - TAVILY_API_KEY=tvly-your-key-here"
        echo ""
    else
        echo "⚠️  No .env file found. Create one with:"
        echo "   OPENAI_API_KEY=your-openai-key"
        echo "   TAVILY_API_KEY=your-tavily-key"
        echo ""
    fi
else
    echo "✅ .env file exists"
    echo ""
fi

# Run tests
echo "🧪 Running tests..."
poetry run pytest tests/ -v

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "⚠️  Some tests failed, but you can continue"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Add your API keys to .env file"
echo "  2. Activate the environment: poetry shell"
echo "  3. Run the demo: python main.py"
echo ""
echo "For more information, see README.md or QUICKSTART.md"

